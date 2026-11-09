"""Count complete requests using the pinned tokenizer and actual chat template."""
from functools import lru_cache
from pathlib import Path
import copy,hashlib,json,os
from inference.test1.token_contract import TokenContractError


@lru_cache(maxsize=2)
def load(tokenizer_path,template_path):
    from tokenizers import Tokenizer
    from jinja2.sandbox import ImmutableSandboxedEnvironment
    from jinja2 import TemplateError
    raw=Path(tokenizer_path).read_bytes()
    if hashlib.sha256(raw).hexdigest()!='06b9509352d2af50381ab2247e083b80d32d5c0aba91c272ca9ff729b6a0e523':
        raise TokenContractError('Pinned target tokenizer hash differs')
    environment=ImmutableSandboxedEnvironment(trim_blocks=True,lstrip_blocks=True,extensions=['jinja2.ext.loopcontrols'])
    def fail(message):raise TemplateError(message)
    environment.globals['raise_exception']=fail
    # Match Transformers chat-template serialization, including Unicode and spaces.
    environment.filters['tojson']=lambda value,**kwargs:json.dumps(value,ensure_ascii=False,**kwargs)
    return Tokenizer.from_str(raw.decode('utf-8')),environment.from_string(Path(template_path).read_text(encoding='utf-8'))


def configured():
    return os.environ.get('TEST1_REQUIRE_EXACT_TOKENIZER')=='1'


def count(messages,tools,template_kwargs,image_cost):
    tokenizer_path=os.environ.get('TEST1_TOKENIZER_FILE')
    template_path=os.environ.get('TEST1_CHAT_TEMPLATE_FILE')
    if not tokenizer_path or not template_path:raise TokenContractError('Exact tokenizer/template paths were not configured before inference')
    try:
        tokenizer,template=load(tokenizer_path,template_path)
        normalized=copy.deepcopy(messages)
        expansion=0
        for message in normalized:
            for call in message.get('tool_calls') or []:
                function=call.get('function',call)
                arguments=function.get('arguments')
                if isinstance(arguments,str):function['arguments']=json.loads(arguments)
            content=message.get('content')
            for part in content if isinstance(content,list) else []:
                if isinstance(part,dict) and part.get('type')=='image_url':
                    # Template already emits start, one pad token, and end.
                    expansion+=image_cost(part)-3
        rendered=template.render(messages=normalized,tools=tools,add_generation_prompt=True,**template_kwargs)
        return len(tokenizer.encode(rendered,add_special_tokens=False).ids)+expansion
    except TokenContractError:raise
    except Exception as exc:raise TokenContractError('Exact token rendering failed: '+type(exc).__name__+': '+str(exc)) from exc
