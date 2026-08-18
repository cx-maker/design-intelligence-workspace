from pathlib import Path

root = Path.cwd()
tsx = root / "features/workspace/workspace-shell.tsx"
api = root / "app/api/design/route.ts"
css = root / "features/workspace/workspace-shell.css"

def rep(s, old, new, label, count=1):
    if old not in s:
        raise SystemExit(f"[失败] 找不到替换点：{label}")
    return s.replace(old, new, count)

# ---------- TSX ----------
s = tsx.read_text(encoding="utf-8")

s = rep(
    s,
    'type Material = { id: string; name: string; description: string; referenceName?: string; referenceUrl?: string; enabled?: boolean; width?: number; height?: number; unit?: "mm"|"px"; sizePreset?: string; copy?: string; withText?: boolean };',
    'type PaletteChoice = "auto"|"white"|"black"|"brand"|"aux1"|"aux2";\ntype Material = { id: string; name: string; description: string; referenceName?: string; referenceUrl?: string; enabled?: boolean; width?: number; height?: number; unit?: "mm"|"px"; sizePreset?: string; copy?: string; withText?: boolean; backgroundPreference?: PaletteChoice; graphicPreference?: PaletteChoice };',
    "material palette fields"
)

# defaults
s = s.replace('withText:true },', 'withText:true, backgroundPreference:"auto", graphicPreference:"auto" },', 3)

# helper before MaterialSetup
needle = 'function MaterialSetup({materials,onChange,compact=false}:{materials:Material[];onChange:(x:Material[])=>void;compact?:boolean}){'
helper = '''function paletteLabel(v:PaletteChoice){
  return v==="auto"?"自动":v==="white"?"白色":v==="black"?"黑色":v==="brand"?"品牌主色":v==="aux1"?"辅助色 1":"辅助色 2";
}
function resolvePalette(v:PaletteChoice|undefined,brandColor:string,auxiliaryColors:string[]){
  if(!v||v==="auto")return "";
  if(v==="white")return "#FFFFFF";
  if(v==="black")return "#111111";
  if(v==="brand")return brandColor;
  if(v==="aux1")return auxiliaryColors[0]||brandColor;
  return auxiliaryColors[1]||auxiliaryColors[0]||brandColor;
}
function PaletteSelect({value,onChange}:{value?:PaletteChoice;onChange:(v:PaletteChoice)=>void}){
  return <select value={value||"auto"} onChange={e=>onChange(e.target.value as PaletteChoice)}>
    {(["auto","white","black","brand","aux1","aux2"] as PaletteChoice[]).map(v=><option key={v} value={v}>{paletteLabel(v)}</option>)}
  </select>;
}

'''
if needle not in s:
    raise SystemExit("[失败] 找不到 MaterialSetup")
s = s.replace(needle, helper + needle, 1)

# Add palette controls to MaterialSetup before text-mode-switch
old = '<div className="text-mode-switch"><span>文字信息</span><button type="button"'
new = '''<div className="material-palette-row">
  <label>底色<PaletteSelect value={m.backgroundPreference} onChange={v=>update(m.id,{backgroundPreference:v})}/></label>
  <label>图形 / Logo 色<PaletteSelect value={m.graphicPreference} onChange={v=>update(m.id,{graphicPreference:v})}/></label>
  <small>“自动”交给 AI；指定后会作为当前物料的优先配色约束。</small>
</div><div className="text-mode-switch"><span>文字信息</span><button type="button"'''
s = rep(s, old, new, "MaterialSetup palette row")

# Add palette prefs to callAi material payload
s = rep(
    s,
    'copy:m.copy,withText:m.withText!==false}))',
    'copy:m.copy,withText:m.withText!==false,backgroundPreference:m.backgroundPreference||"auto",graphicPreference:m.graphicPreference||"auto"}))',
    "AI material palette payload"
)

# Pending material palette row
old_pending = '<div className="text-mode-switch"><button className={m.withText!==false?"selected":""}'
new_pending = '''<div className="pending-palette">
  <label>底色<PaletteSelect value={m.backgroundPreference} onChange={v=>updateMaterial(m.id,{backgroundPreference:v})}/></label>
  <label>图形色<PaletteSelect value={m.graphicPreference} onChange={v=>updateMaterial(m.id,{graphicPreference:v})}/></label>
</div><div className="text-mode-switch"><button className={m.withText!==false?"selected":""}'''
s = rep(s, old_pending, new_pending, "pending palette")

# Pass colors into preview
s = rep(
    s,
    '<DesignPreview layout={l} graphic={graphic} material={m} fallbackIndex={i}/>',
    '<DesignPreview layout={l} graphic={graphic} material={m} fallbackIndex={i} brandColor={brandColor} auxiliaryColors={auxiliaryColors}/>',
    "DesignPreview color props"
)

# Generated result palette controls after size editor
old_size_end = '</div>\n            <span>{l?.concept||m.description||`AI 自由发挥'
new_size_end = '''</div>
            <div className="result-palette-editor">
              <label>底色<PaletteSelect value={m.backgroundPreference} onChange={v=>updateMaterial(m.id,{backgroundPreference:v})}/></label>
              <label>图形色<PaletteSelect value={m.graphicPreference} onChange={v=>updateMaterial(m.id,{graphicPreference:v})}/></label>
              <small>修改后预览即时更新；点“重做”会把新配色约束交给 AI。</small>
            </div>
            <input className="editable-concept" value={l?.concept||""} onChange={e=>setLayouts(prev=>({...prev,[m.id]:{...prev[m.id],concept:e.target.value}}))} placeholder="方案概念 / 描述标题"/>
            <textarea className="editable-rationale" value={l?.rationale||""} onChange={e=>setLayouts(prev=>({...prev,[m.id]:{...prev[m.id],rationale:e.target.value}}))} placeholder="设计说明，可直接编辑后再作为后续调整依据"/>
            <span className="material-desc">{m.description||`AI 自由发挥'''
s = rep(s, old_size_end, new_size_end, "editable description fields")

# remove old rationale duplicate
s = s.replace('{l?.rationale&&<small className="ai-rationale">{l.rationale}</small>}', '')

# Replace DesignPreview signature and sizing/render
old_preview_head = '''function DesignPreview({layout,graphic,material,fallbackIndex}:{layout?:DesignLayout;graphic:AssetFile|null;material:Material;fallbackIndex:number}){
  const bg=layout?.backgroundColor||(fallbackIndex%3===0?'#111111':fallbackIndex%3===1?'#FFFFFF':'#008FDB');
  const pos=layout?.textPosition||'bottom-left';
  const color=layout?.textColor||(bg==='#FFFFFF'?'#111111':'#FFFFFF');
  const w=Math.max(1,material.width||90);
  const h=Math.max(1,material.height||54);
  const ratio=w/h;
  const planeStyle:CSSProperties = ratio>=1
    ? {width:"76%",aspectRatio:`${w}/${h}`,maxHeight:"82%"}
    : {height:"82%",aspectRatio:`${w}/${h}`,maxWidth:"76%"};'''

new_preview_head = '''function DesignPreview({layout,graphic,material,fallbackIndex,brandColor,auxiliaryColors}:{layout?:DesignLayout;graphic:AssetFile|null;material:Material;fallbackIndex:number;brandColor:string;auxiliaryColors:string[]}){
  const preferredBg=resolvePalette(material.backgroundPreference,brandColor,auxiliaryColors);
  const bg=preferredBg||layout?.backgroundColor||(fallbackIndex%3===0?'#111111':fallbackIndex%3===1?'#FFFFFF':brandColor);
  const preferredGraphic=resolvePalette(material.graphicPreference,brandColor,auxiliaryColors);
  const pos=layout?.textPosition||'bottom-left';
  const color=layout?.textColor||(bg==='#FFFFFF'?'#111111':'#FFFFFF');
  const w=Math.max(1,material.width||90);
  const h=Math.max(1,material.height||54);
  const ratio=w/h;

  // 画板比例 + 物理尺寸都参与预览：不再让 90mm 名片和 420mm 手提袋视觉上同样大。
  const mmFactor=material.unit==="px"?0.264583:1;
  const physicalMax=Math.max(w,h)*mmFactor;
  const normalized=Math.max(0,Math.min(1,physicalMax/420));
  const displayMax=34+48*normalized;
  const planeStyle:CSSProperties = ratio>=1
    ? {width:`${displayMax}%`,aspectRatio:`${w}/${h}`,maxHeight:"86%"}
    : {height:`${displayMax}%`,aspectRatio:`${w}/${h}`,maxWidth:"82%"};'''
s = rep(s, old_preview_head, new_preview_head, "DesignPreview physical sizing")

old_logo = '''      {graphic&&<img className="ai-logo" src={graphic.url} alt="" style={{
        left:`${layout?.logoX??65}%`,
        top:`${layout?.logoY??45}%`,
        width:`${Math.max(20,(layout?.logoScale??2)*28)}%`,
        transform:`translate(-50%,-50%) rotate(${layout?.logoRotation??0}deg)`
      }}/>}'''

new_logo = '''      {graphic&&(preferredGraphic?
        <span className="ai-logo ai-logo-mask" aria-label="Logo" style={{
          left:`${layout?.logoX??65}%`,
          top:`${layout?.logoY??45}%`,
          width:`${Math.max(20,(layout?.logoScale??2)*28)}%`,
          aspectRatio:"1",
          background:preferredGraphic,
          WebkitMaskImage:`url("${graphic.url}")`,
          maskImage:`url("${graphic.url}")`,
          WebkitMaskRepeat:"no-repeat",maskRepeat:"no-repeat",
          WebkitMaskPosition:"center",maskPosition:"center",
          WebkitMaskSize:"contain",maskSize:"contain",
          transform:`translate(-50%,-50%) rotate(${layout?.logoRotation??0}deg)`
        } as CSSProperties}/>:
        <img className="ai-logo" src={graphic.url} alt="" style={{
          left:`${layout?.logoX??65}%`,
          top:`${layout?.logoY??45}%`,
          width:`${Math.max(20,(layout?.logoScale??2)*28)}%`,
          transform:`translate(-50%,-50%) rotate(${layout?.logoRotation??0}deg)`
        }}/>)
      }'''
s = rep(s, old_logo, new_logo, "graphic color mask")

tsx.write_text(s, encoding="utf-8")

# ---------- API prompt ----------
r = api.read_text(encoding="utf-8")
r = rep(
    r,
    '6. 色彩严格服从 ratios 权重，不要逐张随机换色。',
    '6. 色彩严格服从 ratios 权重，不要逐张随机换色。每个 material 若 backgroundPreference / graphicPreference 不是 auto，则该物料必须优先服从该配色偏好；brand 对应品牌主色，aux1 / aux2 对应辅助色，white / black 对应黑白。auto 才允许依据 ratios 自主判断。',
    "API palette instruction"
)
r = rep(
    r,
    '3. 严格尊重每个物料的 width / height / unit，把它当真实画布比例。',
    '3. 严格尊重每个物料的 width / height / unit，把它当真实画布比例与真实尺寸边界；不仅比例要正确，还要让信息密度、Logo 相对尺度和留白量符合该物料实际大小。',
    "API physical size instruction"
)
api.write_text(r, encoding="utf-8")

# ---------- CSS ----------
c = css.read_text(encoding="utf-8")
addon = r'''

/* v7.4 — physical size + palette guidance + editable rationale */
.material-palette-row,.pending-palette,.result-palette-editor{display:flex;align-items:flex-end;gap:8px;flex-wrap:wrap}
.material-palette-row{padding:9px 0;border-top:1px solid var(--line);border-bottom:1px solid var(--line)}
.material-palette-row label,.pending-palette label,.result-palette-editor label{display:grid;gap:4px;font-size:8px;opacity:.9}
.material-palette-row select,.pending-palette select,.result-palette-editor select{min-width:105px}
.material-palette-row small,.result-palette-editor small{font-size:8px;opacity:.45}
.result-palette-editor{margin:7px 0 8px}
.editable-concept,.editable-rationale{width:100%;box-sizing:border-box;background:rgba(255,255,255,.025);border:1px solid var(--line);color:inherit;border-radius:6px}
.editable-concept{font-weight:700;padding:7px 8px;margin-top:4px}
.editable-rationale{min-height:76px;padding:8px;resize:vertical;line-height:1.5;margin-top:6px}
.material-desc{display:block;margin-top:6px;opacity:.48;font-size:8px}
.ai-logo-mask{position:absolute;display:block}
'''
if "v7.4 — physical size" not in c:
    c += addon
css.write_text(c, encoding="utf-8")

print("完成：")
print("✓ 第四步预览不再只看宽高比，也按实际尺寸缩放；90mm 名片会明显小于 420mm 手提袋")
print("✓ 每个物料增加底色 / 图形色引导：自动、白、黑、品牌主色、辅助色 1、辅助色 2")
print("✓ 配色选择即时影响预览，并在重做/生成时进入 AI 指令")
print("✓ 指定图形色时使用 SVG mask 统一着色；自动模式保留原始 Logo")
print("✓ 右侧方案概念和设计说明改为可直接编辑")
print("✓ AI Prompt 强化真实尺寸和配色优先级")
print("下一步运行：npm run build")
