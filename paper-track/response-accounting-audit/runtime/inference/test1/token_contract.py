"""Request invariants and compact metadata; never logs keys or full prompts."""
from pathlib import Path
import hashlib
import json
import os
import time
import uuid


class TokenContractError(ValueError):
    pass


def attach_memory(history,capsule):
    """Keep memory inside the real query, never as a replacement user turn."""
    history=list(history)
    for index in range(len(history)-1,-1,-1):
        message=history[index]
        if message.get('role')!='user': continue
        message=dict(message)
        previous=message.get('_test1_memory_injection','')
        content=message.get('content','')
        if isinstance(content,str):
            if previous and previous not in content: raise TokenContractError('memory injection metadata differs from query')
            content=content.replace(previous,'',1) if previous else content
            message['content']=content+capsule
        elif isinstance(content,list):
            parts=[];removed=not previous
            for part in content:
                if isinstance(part,dict) and part.get('type')=='text' and previous and previous in part.get('text',''):
                    part={**part,'text':part['text'].replace(previous,'',1)};removed=True
                    if not part['text']: continue
                parts.append(part)
            if not removed: raise TokenContractError('memory injection metadata differs from multimodal query')
            message['content']=[*parts,{'type':'text','text':capsule}]
        else: raise TokenContractError('unsupported current-query content')
        message['_test1_memory_injection']=capsule
        history[index]=message
        return history
    raise TokenContractError('cannot restore memory without a user query')


def validate_messages(messages):
    if not isinstance(messages,list) or not any(m.get('role')=='user' for m in messages):
        raise TokenContractError('request has no user query')
    pending=set()
    for message in messages:
        role=message.get('role')
        if role=='assistant':
            if pending:
                raise TokenContractError('unanswered tool calls before next assistant message')
            for call in message.get('tool_calls') or []:
                identifier=call.get('id')
                if not identifier or identifier in pending:
                    raise TokenContractError('missing/duplicate tool call id')
                arguments=call.get('function',{}).get('arguments','{}')
                try:
                    parsed=json.loads(arguments) if isinstance(arguments,str) else arguments
                    if not isinstance(parsed,dict): raise ValueError('arguments must be an object')
                except (ValueError,TypeError) as exc:
                    raise TokenContractError('malformed tool-call arguments in history') from exc
                pending.add(identifier)
        elif role=='tool':
            identifier=message.get('tool_call_id')
            if identifier not in pending:
                raise TokenContractError('orphaned or duplicate tool result')
            pending.remove(identifier)
        elif pending:
            raise TokenContractError('tool-call/result block interrupted')
    if pending:
        raise TokenContractError('request contains unanswered tool calls')


def check_effective(module,agent=None):
    context=int(module._LOCAL_ANALYZER_CONTEXT_WINDOW)
    output=int(module._LOCAL_ANALYZER_MAX_OUTPUT)
    safety=int(module._REQUEST_SAFETY_MARGIN_TOKENS)
    server=int(os.environ.get('TEST1_SERVER_CONTEXT',context))
    if context<=output+safety or context>server:
        raise TokenContractError('incompatible server/harness/output capacity')
    if os.environ.get('TEST1_VALIDATE_EFFECTIVE_CONFIG')=='1':
        if context!=int(os.environ['LOCAL_ANALYZER_CONTEXT_WINDOW']) or output!=int(os.environ['LOCAL_ANALYZER_MAX_OUTPUT']):
            raise TokenContractError('imported token limits differ from configured environment; restart kernel')
        if agent is not None and (agent._context_budget_tokens!=context-agent._reply_reserve_tokens-safety or agent._max_output_tokens!=output):
            raise TokenContractError('agent instance token limits differ from imported configuration')
    return {'module':module.__file__,'harness_context':context,'server_context':server,
        'max_output':output,'safety':safety,'derived_input_budget':context-output-safety}


class RequestTrace:
    def __init__(self,agent,payload,estimate):
        validate_messages(payload.get('messages',[]))
        budget=agent._context_budget_tokens
        if estimate>budget:
            raise TokenContractError(f'irreducible request estimate {estimate} exceeds input budget {budget}')
        output=payload.get('max_tokens')
        if type(output) is not int or not 0<output<=agent._reply_reserve_tokens:
            raise TokenContractError('request output limit exceeds reserved reply capacity')
        self.identifier=uuid.uuid4().hex
        self.attempt=0
        state=getattr(agent,'_session_state_path',None)
        self.path=Path(state).with_name(Path(state).stem+'_token_trace.jsonl') if state else None
        images=[]
        for message in payload['messages']:
            for part in message.get('content',[]) if isinstance(message.get('content'),list) else []:
                if isinstance(part,dict) and part.get('type')=='image_url': images.append(1)
        self.meta={'client_request_id':self.identifier,'estimated_input_tokens':estimate,
            'estimator':'pinned_tokenizer_and_chat_template' if os.environ.get('TEST1_REQUIRE_EXACT_TOKENIZER')=='1' else 'legacy_calibrated_heuristic',
            'input_budget':budget,'max_tokens':output,'reply_reserve':agent._reply_reserve_tokens,
            'image_count':len(images),'message_count':len(payload['messages']),
            'message_sha256':hashlib.sha256(json.dumps(payload['messages'],sort_keys=True).encode()).hexdigest(),
            'chat_template_kwargs':payload.get('chat_template_kwargs',{})}
        self.emit('request')

    def emit(self,event,**data):
        if self.path:
            with self.path.open('a',encoding='utf-8') as file:
                file.write(json.dumps({'event':event,'epoch':time.time(),**self.meta,**data})+'\n')

    def post(self,post,*args,**kwargs):
        self.attempt+=1
        started=time.monotonic()
        self.emit('attempt',attempt=self.attempt)
        try:
            response=post(*args,**kwargs)
        except BaseException as exc:
            self.emit('transport_error',attempt=self.attempt,error_type=type(exc).__name__,elapsed=time.monotonic()-started,usage_known=False)
            raise
        self.emit('headers',attempt=self.attempt,status=response.status_code,elapsed=time.monotonic()-started)
        return response

    def result(self,payload):
        self.emit('response',attempt=self.attempt,server_response_id=payload.get('id'),usage=payload.get('usage'),
            finish_reason=(payload.get('choices') or [{}])[0].get('finish_reason'))
