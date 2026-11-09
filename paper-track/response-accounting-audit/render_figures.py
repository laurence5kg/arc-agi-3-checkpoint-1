"""Render all retention observations from public aggregate data; no model or API calls."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

def render(root):
    pairs=json.loads((root/'figure_data.json').read_text(encoding='utf-8'))['retention']['pairs']
    games=['ar25','bp35','lp85','re86','sk48']
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9.5,'axes.spines.top':False,'axes.spines.right':False})
    fig,ax=plt.subplots(figsize=(7.4,3.3))
    for i,g in enumerate(games):
        for block in [1,2]:
            r=next(r for r in pairs if r['game'].startswith(g+'-') and r['block']==block)
            y=i+(-.15 if block==1 else .15)
            ax.plot([r['A'],r['B']],[y,y],color='#a9b5c3',lw=1.6,zorder=1)
            ax.scatter([r['A']],[y],s=30,color='#197b85',zorder=3)
            ax.scatter([r['B']],[y],s=65,marker='D',facecolors='none',edgecolors='#c17a17',linewidths=1.4,zorder=4)
            ax.text(105,y,str(block),va='center',fontsize=8,color='#52667a')
    ax.set_yticks(range(5),games);ax.invert_yaxis();ax.set_xlim(-4,110)
    ax.set_xticks([0,20,40,60,80,100]);ax.set_xlabel('Public stress-screen episode score')
    ax.grid(axis='x',alpha=.18);ax.set_axisbelow(True)
    handles=[Line2D([],[],marker='o',ls='',color='#197b85',label='Notes off'),Line2D([],[],marker='D',ls='',markerfacecolor='none',color='#c17a17',label='Notes on')]
    ax.legend(handles=handles,ncol=2,loc='lower left',bbox_to_anchor=(0,1.02),frameon=False)
    ax.text(105,-.58,'Block',ha='center',fontsize=8,color='#52667a')
    fig.tight_layout(pad=1)
    folder=root/'figures';folder.mkdir(exist_ok=True)
    for ext in ['png','svg']:fig.savefig(folder/f'retention_episodes.{ext}',dpi=190)
    plt.close(fig)
    # Cover is typography and aggregate results, not another scientific claim.
    fig=plt.figure(figsize=(10,5.25),facecolor='#102737')
    fig.text(.07,.77,'AUDITING TOKENS\nAND TOOL DISPATCH',color='white',size=25,weight='bold',linespacing=1.25)
    fig.text(.07,.43,'ARC-AGI-3 | Jiayi Zhang',color='#acd7d8',size=14)
    fig.text(.07,.26,'29 capped tool responses  |  8 parseable  |  1 recorded action',color='white',size=13)
    fig.text(.07,.13,'Saved-evidence audit; no established score improvement',color='#b9c7d1',size=11)
    fig.savefig(folder/'cover_audit.png',dpi=150,facecolor=fig.get_facecolor());plt.close(fig)

if __name__=='__main__':render(Path(__file__).resolve().parent)
