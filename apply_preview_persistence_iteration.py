from pathlib import Path

root=Path.cwd()
ws=root/"features/workspace/workspace-shell.tsx"
css=root/"features/workspace/workspace-shell.css"

def rep(s,a,b,label):
    if a not in s:
        raise SystemExit(f"[失败] 找不到替换点：{label}")
    return s.replace(a,b,1)

s=ws.read_text(encoding="utf-8")

s=rep(s,
'''  const [generated,setGenerated]=useState(false); const [generating,setGenerating]=useState(false); const [approved,setApproved]=useState<string[]>([]); const [deleted,setDeleted]=useState<string[]>([]);
  const [currentModel,setCurrentModel]=useState("");''',
'''  const [generated,setGenerated]=useState(false); const [generating,setGenerating]=useState(false); const [approved,setApproved]=useState<string[]>([]); const [deleted,setDeleted]=useState<string[]>([]);
  const [layouts,setLayouts]=useState<Record<string,DesignLayout>>({});
  const [currentModel,setCurrentModel]=useState("");''',
"父级 layouts")

s=rep(s,
'''    setMaterials(defaultMaterials.map(x=>({...x}))); setRulesConfirmed(false); setSelectedRouteId(""); setGenerated(false); setGenerating(false); setApproved([]); setDeleted([]);''',
'''    setMaterials(defaultMaterials.map(x=>({...x}))); setRulesConfirmed(false); setSelectedRouteId(""); setGenerated(false); setGenerating(false); setApproved([]); setDeleted([]); setLayouts({});''',
"reset layouts")

s=rep(s,
'''materials={materials} setMaterials={setMaterials} selectedExtensions={selectedExtensions} approved={approved}''',
'''materials={materials} setMaterials={setMaterials} layouts={layouts} setLayouts={setLayouts} selectedExtensions={selectedExtensions} approved={approved}''',
"传递 layouts")

s=rep(s,
'''function GenerateAndReview({graphic,brandColor,auxiliaryColors,ratios,selectedBoundaries,materials,setMaterials,selectedExtensions,approved,setApproved,deleted,setDeleted,generating,setGenerating,generated,setGenerated,currentModel,selectedRoute}:{graphic:AssetFile|null;brandColor:string;auxiliaryColors:string[];ratios:Ratios;selectedBoundaries:string[];materials:Material[];setMaterials:(x:Material[])=>void;selectedExtensions:string[];approved:string[];setApproved:(x:string[])=>void;deleted:string[];setDeleted:(x:string[])=>void;generating:boolean;setGenerating:(x:boolean)=>void;generated:boolean;setGenerated:(x:boolean)=>void;currentModel:string;selectedRoute:DeconstructionRoute|null}){
  const [layouts,setLayouts]=useState<Record<string,DesignLayout>>({});''',
'''function GenerateAndReview({graphic,brandColor,auxiliaryColors,ratios,selectedBoundaries,materials,setMaterials,layouts,setLayouts,selectedExtensions,approved,setApproved,deleted,setDeleted,generating,setGenerating,generated,setGenerated,currentModel,selectedRoute}:{graphic:AssetFile|null;brandColor:string;auxiliaryColors:string[];ratios:Ratios;selectedBoundaries:string[];materials:Material[];setMaterials:(x:Material[])=>void;layouts:Record<string,DesignLayout>;setLayouts:(x:Record<string,DesignLayout>)=>void;selectedExtensions:string[];approved:string[];setApproved:(x:string[])=>void;deleted:string[];setDeleted:(x:string[])=>void;generating:boolean;setGenerating:(x:boolean)=>void;generated:boolean;setGenerated:(x:boolean)=>void;currentModel:string;selectedRoute:DeconstructionRoute|null}){''',
"GenerateAndReview layouts")

s=s.replace('setLayouts(prev=>({...prev,[m.id]:out[0]}));','setLayouts({...layouts,[m.id]:out[0]});')
s=s.replace('setLayouts(prev=>({...prev,[target.id]:out[0]}));','setLayouts({...layouts,[target.id]:out[0]});')

s=rep(s,
'''  const [editing,setEditing]=useState<Material|null>(null);
  const [adjustText,setAdjustText]=useState("");''',
'''  const [editing,setEditing]=useState<Material|null>(null);
  const [copyEditing,setCopyEditing]=useState<Material|null>(null);
  const [copyDraft,setCopyDraft]=useState({headline:"",subline:"",microcopy:""});
  const [adjustText,setAdjustText]=useState("");''',
"文字编辑 state")

s=s.replace('<DesignPreview layout={l} graphic={graphic} fallbackIndex={i}/>','<DesignPreview layout={l} graphic={graphic} material={m} fallbackIndex={i}/>')

s=rep(s,
'''<button onClick={()=>{setEditing(m);setAdjustText("")}} disabled={isBusy}>调整</button>
              <button onClick={()=>redo(m)} disabled={isBusy}>{isBusy?"生成中…":"重做"}</button>''',
'''<button onClick={()=>{setEditing(m);setAdjustText("")}} disabled={isBusy}>调整</button>
              <button onClick={()=>{const x=layouts[m.id];setCopyEditing(m);setCopyDraft({headline:x?.headline||"",subline:x?.subline||"",microcopy:x?.microcopy||""})}} disabled={isBusy}>文字</button>
              <button onClick={()=>redo(m)} disabled={isBusy}>{isBusy?"生成中…":"重做"}</button>''',
"文字按钮")

marker='''    </div>}
  </div>;
}

function DesignPreview'''
copy_overlay='''    </div>}

    {copyEditing&&<div className="adjust-overlay" onClick={()=>setCopyEditing(null)}>
      <div className="adjust-panel copy-panel" onClick={e=>e.stopPropagation()}>
        <span className="rule-tag">文字信息 · {copyEditing.name}</span>
        <h3>直接修改这张平面里的文字。</h3>
        <p>这里只改文字内容，不重新调用 AI，也不改变 Logo、网格和版式结构。</p>
        <label>主标题<input value={copyDraft.headline} onChange={e=>setCopyDraft({...copyDraft,headline:e.target.value})}/></label>
        <label>副信息<textarea value={copyDraft.subline} onChange={e=>setCopyDraft({...copyDraft,subline:e.target.value})}/></label>
        <label>微型信息<input value={copyDraft.microcopy} onChange={e=>setCopyDraft({...copyDraft,microcopy:e.target.value})}/></label>
        <div className="adjust-actions">
          <button className="secondary" onClick={()=>setCopyEditing(null)}>取消</button>
          <button className="primary" onClick={()=>{const old=layouts[copyEditing.id];if(old)setLayouts({...layouts,[copyEditing.id]:{...old,...copyDraft}});setCopyEditing(null)}}>保存文字</button>
        </div>
      </div>
    </div>}
  </div>;
}

function DesignPreview'''
s=rep(s,marker,copy_overlay,"文字编辑弹窗")

start=s.find("function DesignPreview(")
end=s.find("\nfunction ",start+10)
if start<0 or end<0:
    raise SystemExit("[失败] 找不到 DesignPreview")
new_preview='''function DesignPreview({layout,graphic,material,fallbackIndex}:{layout?:DesignLayout;graphic:AssetFile|null;material:Material;fallbackIndex:number}){
  const bg=layout?.backgroundColor||(fallbackIndex%3===0?'#111111':fallbackIndex%3===1?'#FFFFFF':'#008FDB');
  const pos=layout?.textPosition||'bottom-left';
  const color=layout?.textColor||(bg==='#FFFFFF'?'#111111':'#FFFFFF');
  const w=Math.max(1,material.width||90), h=Math.max(1,material.height||54);
  const ratio=w/h;
  const style:CSSProperties = ratio>=1
    ? {width:"78%",aspectRatio:`${w}/${h}`,maxHeight:"82%"}
    : {height:"82%",aspectRatio:`${w}/${h}`,maxWidth:"78%"};
  return <div className="material-artboard">
    <div className="material-plane ai-design-preview" style={{...style,background:bg}}>
      {graphic&&<img className="ai-logo" src={graphic.url} alt="" style={{left:`${layout?.logoX??65}%`,top:`${layout?.logoY??45}%`,width:`${Math.max(20,(layout?.logoScale??2)*28)}%`,transform:`translate(-50%,-50%) rotate(${layout?.logoRotation??0}deg)`}}/>}
      <div className={`ai-copy ${pos}`} style={{color,textAlign:layout?.textAlign||"left"}}>
        <small>{layout?.microcopy||"BRAND SYSTEM / 01"}</small>
        <strong>{layout?.headline||layout?.concept||"Identity through form."}</strong>
        <span>{layout?.subline||"A consistent visual language built from one recognizable mark."}</span>
      </div>
      <em className="material-size-tag">{material.width||90} × {material.height||54} {material.unit||"mm"}</em>
    </div>
  </div>
}'''
s=s[:start]+new_preview+s[end:]
ws.write_text(s,encoding="utf-8")

c=css.read_text(encoding="utf-8")
addon='''

/* v6.7 — physical artboard preview + editable copy */
.material-artboard{
  width:100%;height:100%;min-height:220px;
  display:grid;place-items:center;
  background:#d7d9db;
  overflow:hidden;
  padding:18px;
}
.dark .material-artboard{background:#bfc2c5}
.material-plane{
  position:relative!important;
  flex:none!important;
  overflow:hidden;
  border-radius:2px;
  box-shadow:0 2px 12px rgba(0,0,0,.12);
}
.material-size-tag{
  position:absolute;right:7px;bottom:6px;
  font-size:6px;font-style:normal;opacity:.38;
}
.preview-loading-wrap>.material-artboard{height:100%}
.copy-panel label{
  display:grid;gap:6px;margin-top:10px;
  font-size:10px;color:var(--muted)
}
.copy-panel input,.copy-panel textarea{
  width:100%;border:1px solid var(--line);
  border-radius:7px;background:transparent;color:inherit;
  padding:10px;font:inherit
}
.copy-panel textarea{min-height:72px;resize:vertical}
'''
if "physical artboard preview + editable copy" not in c:
    css.write_text(c+addon,encoding="utf-8")

print("完成：修复第四步返回后结果丢失，并加入真实物料画板预览 + 文字编辑。")
print("下一步：npm run build")
