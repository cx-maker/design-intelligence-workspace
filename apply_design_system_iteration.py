from pathlib import Path

root = Path.cwd()
ws = root / "features/workspace/workspace-shell.tsx"
api = root / "app/api/design/route.ts"
css = root / "features/workspace/workspace-shell.css"

def rep(text, old, new, label):
    if old not in text:
        raise SystemExit(f"[失败] 找不到替换点：{label}。请确认本地 main 已更新。")
    return text.replace(old, new, 1)

s = ws.read_text(encoding="utf-8")

s = rep(s,
'type Material = { id: string; name: string; description: string; referenceName?: string; referenceUrl?: string };',
'type Material = { id: string; name: string; description: string; referenceName?: string; referenceUrl?: string; enabled?: boolean; width?: number; height?: number; unit?: "mm"|"px"; sizePreset?: string; copy?: string };',
"Material 类型")

s = rep(s,
'type DesignLayout = { materialId:string; concept:string; backgroundColor:string; logoScale:number; logoX:number; logoY:number; logoRotation:number; textPosition:"top-left"|"top-right"|"bottom-left"|"bottom-right"; textColor:string; rationale:string };',
'type DesignLayout = { materialId:string; concept:string; backgroundColor:string; logoScale:number; logoX:number; logoY:number; logoRotation:number; textPosition:"top-left"|"top-right"|"bottom-left"|"bottom-right"; textColor:string; headline:string; subline:string; microcopy:string; textAlign:"left"|"center"|"right"; rationale:string };',
"DesignLayout 类型")

s = rep(s,
'''const defaultMaterials: Material[] = [
  { id: "card", name: "名片", description: "" }, { id: "bag", name: "手提袋", description: "" }, { id: "box", name: "包装盒", description: "" },
];''',
'''const defaultMaterials: Material[] = [
  { id:"card", name:"名片", description:"建立品牌最基础的信息层级与留白规则。", enabled:true, width:90, height:54, unit:"mm", sizePreset:"90 × 54 mm", copy:"姓名 / 职位 / 电话 / 邮箱 / 品牌信息" },
  { id:"bag", name:"手提袋", description:"验证大尺度 Logo、裁切、色块和短文案关系。", enabled:true, width:320, height:420, unit:"mm", sizePreset:"320 × 420 mm", copy:"品牌名 / 一句品牌短语" },
  { id:"box", name:"包装盒", description:"验证多面信息层级与系统化图形语言。", enabled:true, width:240, height:180, unit:"mm", sizePreset:"240 × 180 mm", copy:"品牌名 / 产品名 / 规格 / 辅助信息" },
];''',
"默认物料")

s = rep(s,
'{step==="references"&&<ConfirmAssets graphic={graphic} cnTexts={cnTexts} enTexts={enTexts} brandColor={brandColor} setBrandColor={setBrandColor} auxiliaryColors={auxiliaryColors} setAuxiliaryColors={setAuxiliaryColors} confirmed={assetsConfirmed} setConfirmed={setAssetsConfirmed}/>}',
'{step==="references"&&<ConfirmAssets graphic={graphic} cnTexts={cnTexts} enTexts={enTexts} brandColor={brandColor} setBrandColor={setBrandColor} auxiliaryColors={auxiliaryColors} setAuxiliaryColors={setAuxiliaryColors} ratios={ratios} setRatios={setRatios} confirmed={assetsConfirmed} setConfirmed={setAssetsConfirmed}/>}','第二步 props')

s = rep(s,
'function ConfirmAssets({graphic,cnTexts,enTexts,brandColor,setBrandColor,auxiliaryColors,setAuxiliaryColors,confirmed,setConfirmed}:{graphic:AssetFile|null;cnTexts:AssetFile[];enTexts:AssetFile[];brandColor:string;setBrandColor:(x:string)=>void;auxiliaryColors:string[];setAuxiliaryColors:(x:string[])=>void;confirmed:boolean;setConfirmed:(x:boolean)=>void})',
'function ConfirmAssets({graphic,cnTexts,enTexts,brandColor,setBrandColor,auxiliaryColors,setAuxiliaryColors,ratios,setRatios,confirmed,setConfirmed}:{graphic:AssetFile|null;cnTexts:AssetFile[];enTexts:AssetFile[];brandColor:string;setBrandColor:(x:string)=>void;auxiliaryColors:string[];setAuxiliaryColors:(x:string[])=>void;ratios:Ratios;setRatios:(x:Ratios)=>void;confirmed:boolean;setConfirmed:(x:boolean)=>void})',
"ConfirmAssets 签名")

s = rep(s,
'</div></section><label className="confirm-check"><input type="checkbox" checked={confirmed}',
'''</div></section><section className="color-panel ratio-panel-step2"><div className="color-panel-head"><div><span>颜色使用比例</span><small>把色板进一步变成系统规则，而不是让 AI 随机配色。</small></div></div><ColorRatio ratios={ratios} setRatios={setRatios} brandColor={brandColor} auxiliaryColors={auxiliaryColors}/></section><label className="confirm-check"><input type="checkbox" checked={confirmed}''',
"第二步颜色比例")

s = rep(s,
'materials,selectedExtensions,approved,setApproved',
'materials,setMaterials,selectedExtensions,approved,setApproved',
"GenerateAndReview 参数名")
s = rep(s,
'materials:Material[];selectedExtensions:string[];',
'materials:Material[];setMaterials:(x:Material[])=>void;selectedExtensions:string[];',
"GenerateAndReview 参数类型")
s = rep(s,
'materials={materials} selectedExtensions={selectedExtensions}',
'materials={materials} setMaterials={setMaterials} selectedExtensions={selectedExtensions}',
"GenerateAndReview 调用")
s = rep(s,
'const visible=materials.filter(m=>!deleted.includes(m.id));',
'const visible=materials.filter(m=>m.enabled!==false&&!deleted.includes(m.id));',
"启用物料过滤")

needle = '''    {error&&<div className="api-error">{error}</div>}

    {!generated&&<button className="primary large generate-btn" onClick={generate} disabled={generating}>'''
s = rep(s, needle, '''    {error&&<div className="api-error">{error}</div>}

    {!generated&&<MaterialSetup materials={materials} onChange={setMaterials}/>}

    {!generated&&<button className="primary large generate-btn" onClick={generate} disabled={generating}>''', "第四步物料设置")

old_preview = '''function DesignPreview({layout,graphic,fallbackIndex}:{layout?:DesignLayout;graphic:AssetFile|null;fallbackIndex:number}){ const bg=layout?.backgroundColor||(fallbackIndex%3===0?'#111111':fallbackIndex%3===1?'#FFFFFF':'#008FDB'); const pos=layout?.textPosition||'bottom-left'; return <div className="ai-design-preview" style={{background:bg}}>{graphic&&<img className="ai-logo" src={graphic.url} alt="" style={{left:`${layout?.logoX??65}%`,top:`${layout?.logoY??45}%`,width:`${Math.max(20,(layout?.logoScale??2)*28)}%`,transform:`translate(-50%,-50%) rotate(${layout?.logoRotation??0}deg)`}}/>}<span className={`ai-caption ${pos}`} style={{color:layout?.textColor||(bg==='#FFFFFF'?'#111111':'#FFFFFF')}}>{layout?.concept||'AI DESIGN'}</span></div>}'''
new_preview = '''function DesignPreview({layout,graphic,fallbackIndex}:{layout?:DesignLayout;graphic:AssetFile|null;fallbackIndex:number}){ const bg=layout?.backgroundColor||(fallbackIndex%3===0?'#111111':fallbackIndex%3===1?'#FFFFFF':'#008FDB'); const pos=layout?.textPosition||'bottom-left'; const color=layout?.textColor||(bg==='#FFFFFF'?'#111111':'#FFFFFF'); return <div className="ai-design-preview" style={{background:bg}}>{graphic&&<img className="ai-logo" src={graphic.url} alt="" style={{left:`${layout?.logoX??65}%`,top:`${layout?.logoY??45}%`,width:`${Math.max(20,(layout?.logoScale??2)*28)}%`,transform:`translate(-50%,-50%) rotate(${layout?.logoRotation??0}deg)`}}/>}<div className={`ai-copy ${pos}`} style={{color,textAlign:layout?.textAlign||"left"}}><small>{layout?.microcopy||"BRAND SYSTEM / 01"}</small><strong>{layout?.headline||layout?.concept||"Identity through form."}</strong><span>{layout?.subline||"A consistent visual language built from one recognizable mark."}</span></div></div>}'''
s = rep(s, old_preview, new_preview, "预览文案层级")

component = r'''
const materialPresets:Record<string,{label:string;width:number;height:number;unit:"mm"|"px"}[]> = {
  "名片":[{label:"90 × 54 mm",width:90,height:54,unit:"mm"},{label:"85 × 55 mm",width:85,height:55,unit:"mm"}],
  "手提袋":[{label:"320 × 420 mm",width:320,height:420,unit:"mm"},{label:"260 × 340 mm",width:260,height:340,unit:"mm"}],
  "包装盒":[{label:"240 × 180 mm",width:240,height:180,unit:"mm"},{label:"200 × 140 mm",width:200,height:140,unit:"mm"}],
  "海报":[{label:"A3 · 297 × 420 mm",width:297,height:420,unit:"mm"},{label:"A2 · 420 × 594 mm",width:420,height:594,unit:"mm"}],
  "社交媒体":[{label:"1080 × 1350 px",width:1080,height:1350,unit:"px"},{label:"1080 × 1080 px",width:1080,height:1080,unit:"px"}],
};
function MaterialSetup({materials,onChange}:{materials:Material[];onChange:(x:Material[])=>void}){
  const update=(id:string,p:Partial<Material>)=>onChange(materials.map(m=>m.id===id?{...m,...p}:m));
  const add=()=>onChange([...materials,{id:`custom-${Date.now()}`,name:"海报",description:"验证版式系统与信息层级。",enabled:true,width:297,height:420,unit:"mm",sizePreset:"A3 · 297 × 420 mm",copy:"品牌主张 / 标题 / 副标题 / 辅助信息"}]);
  const applyPreset=(m:Material,label:string)=>{const p=(materialPresets[m.name]||[]).find(x=>x.label===label);if(p)update(m.id,{...p,sizePreset:p.label});};
  return <section className="material-setup"><div className="material-setup-head"><div><span className="rule-tag">本轮物料与画布</span><h3>先规定尺寸，再让 AI 在真实边界里做设计。</h3><p>同一轮物料共享一套网格、字体层级、图形语法与色彩逻辑，避免每张各做各的。</p></div><button className="secondary" onClick={add}>+ 添加物料</button></div><div className="material-setup-grid">{materials.map((m,index)=><article className={`material-setup-card ${m.enabled===false?"off":""}`} key={m.id}><div className="material-card-top"><label><input type="checkbox" checked={m.enabled!==false} onChange={e=>update(m.id,{enabled:e.target.checked})}/><b>{String(index+1).padStart(2,"0")} · {m.name}</b></label><button className="remove-btn" onClick={()=>onChange(materials.filter(x=>x.id!==m.id))}>删除</button></div><div className="material-row"><label>物料<input value={m.name} onChange={e=>update(m.id,{name:e.target.value,sizePreset:""})}/></label><label>常用尺寸<select value={m.sizePreset||""} onChange={e=>applyPreset(m,e.target.value)}><option value="">自定义</option>{(materialPresets[m.name]||[]).map(p=><option key={p.label} value={p.label}>{p.label}</option>)}</select></label></div><div className="material-row dimensions"><label>宽<input type="number" min="1" value={m.width||0} onChange={e=>update(m.id,{width:Number(e.target.value),sizePreset:""})}/></label><span>×</span><label>高<input type="number" min="1" value={m.height||0} onChange={e=>update(m.id,{height:Number(e.target.value),sizePreset:""})}/></label><label>单位<select value={m.unit||"mm"} onChange={e=>update(m.id,{unit:e.target.value as "mm"|"px"})}><option value="mm">mm</option><option value="px">px</option></select></label></div><label>必须出现的信息<textarea value={m.copy||""} onChange={e=>update(m.id,{copy:e.target.value})} placeholder="例如：品牌名 / 标题 / 副标题 / 日期 / 联系方式"/></label><label>设计要求<textarea value={m.description} onChange={e=>update(m.id,{description:e.target.value})} placeholder="例如：留白大、Logo 可超大裁切，但信息层级必须清晰。"/></label></article>)}</div></section>
}
'''
s = rep(s, "
function GenerateAndReview(", "
"+component+"
function GenerateAndReview(", "物料设置组件")
ws.write_text(s, encoding="utf-8")

a = api.read_text(encoding="utf-8")
a = rep(a,
'required:["materialId","concept","backgroundColor","logoScale","logoX","logoY","logoRotation","textPosition","textColor","rationale"],',
'required:["materialId","concept","backgroundColor","logoScale","logoX","logoY","logoRotation","textPosition","textColor","headline","subline","microcopy","textAlign","rationale"],',
"API schema required")
a = rep(a,
'textColor:{type:"string"},rationale:{type:"string"}',
'textColor:{type:"string"},headline:{type:"string"},subline:{type:"string"},microcopy:{type:"string"},textAlign:{type:"string",enum:["left","center","right"]},rationale:{type:"string"}',
"API schema copy")

old = '''   :`你是品牌视觉延展设计助手。根据已经确定的 Logo 和用户约束，为每个物料生成克制、现代、国际化的二维品牌版式参数。不要重新设计 Logo，只决定原始 Logo 的比例、位置、裁切感、背景和信息位置。品牌约束：${JSON.stringify(context)}。物料：${JSON.stringify(materials)}。参考图只用于感知调性、留白、密度和构图，不复制其中品牌元素。只返回合法 JSON。`;'''
new = '''   :`你是一名资深品牌视觉设计总监。任务不是分别做几张 Logo 放置图，而是先建立一个统一视觉系统，再把同一系统应用到全部物料。
必须遵守：
1. 不重新设计 Logo，不改变原始路径；从 deconstructionRoute 与 selectedExtensions 提取统一视觉语法。
2. 全部物料共享同一套网格、Logo 尺度策略、裁切规则、留白节奏、文字层级、色彩比例与信息密度。
3. 严格尊重每个物料的 width / height / unit，把它当真实画布比例。
4. 不能只有 Logo。每张必须建立至少三级信息：headline、subline、microcopy；基于 material.copy 组织真实感文案，不胡编事实数据。
5. 允许超大尺度、边缘裁切、非对称网格、重复节奏，但必须服从当前路线；避免所有物料都变成 Logo 居中加左下小字。
6. 色彩严格服从 ratios 权重，不要逐张随机换色。
7. 先确定一个 system idea，再输出各物料参数；rationale 说明该物料如何继承统一系统。
8. 参考图只学习调性、留白、密度、信息层级与构图方法，不复制其中品牌元素。
品牌约束：${JSON.stringify(context)}。
物料与真实尺寸：${JSON.stringify(materials)}。
只返回合法 JSON。`;'''
a = rep(a, old, new, "系统化 Prompt")
api.write_text(a, encoding="utf-8")

c = css.read_text(encoding="utf-8")
addon = r'''
/* iteration: material canvas + stronger typographic system */
.ratio-panel-step2{margin-top:12px}
.material-setup{margin:18px 0 22px;border:1px solid var(--line);border-radius:12px;padding:18px;background:var(--panel)}
.material-setup-head{display:flex;justify-content:space-between;gap:24px;align-items:flex-start;margin-bottom:14px}
.material-setup-head h3{margin:7px 0 5px;font-size:18px}.material-setup-head p{margin:0;color:var(--muted);font-size:12px;max-width:620px}
.material-setup-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px}
.material-setup-card{border:1px solid var(--line);border-radius:10px;padding:13px;background:var(--surface);display:flex;flex-direction:column;gap:10px}.material-setup-card.off{opacity:.42}
.material-card-top{display:flex;align-items:center;justify-content:space-between;gap:10px}.material-card-top label{display:flex;align-items:center;gap:7px;flex-direction:row}
.material-row{display:grid;grid-template-columns:1fr 1fr;gap:8px}.material-row.dimensions{grid-template-columns:1fr auto 1fr .8fr;align-items:end}.material-row.dimensions>span{padding-bottom:9px;color:var(--muted)}
.material-setup-card label{font-size:10px;color:var(--muted);display:flex;flex-direction:column;gap:5px}
.material-setup-card input,.material-setup-card select,.material-setup-card textarea{width:100%;border:1px solid var(--line);background:transparent;color:inherit;border-radius:7px;padding:8px;font:inherit}.material-setup-card textarea{min-height:58px;resize:vertical}
.ai-copy{position:absolute;z-index:3;width:38%;display:flex;flex-direction:column;gap:5px;line-height:1.08}.ai-copy.top-left{left:6%;top:7%}.ai-copy.top-right{right:6%;top:7%}.ai-copy.bottom-left{left:6%;bottom:7%}.ai-copy.bottom-right{right:6%;bottom:7%}
.ai-copy small{font-size:7px;letter-spacing:.12em;text-transform:uppercase;opacity:.72}.ai-copy strong{font-size:18px;font-weight:650;letter-spacing:-.035em}.ai-copy span{font-size:8px;line-height:1.35;opacity:.78}
@media(max-width:1000px){.material-setup-grid{grid-template-columns:1fr}.material-setup-head{flex-direction:column}.ai-copy{width:44%}}
'''
if "iteration: material canvas + stronger typographic system" not in c:
    css.write_text(c + addon, encoding="utf-8")

print("完成：已更新 workspace-shell.tsx / route.ts / workspace-shell.css")
print("下一步运行：npm run build")
