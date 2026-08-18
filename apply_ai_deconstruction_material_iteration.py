from pathlib import Path

root = Path.cwd()
tsx = root / "features/workspace/workspace-shell.tsx"
css = root / "features/workspace/workspace-shell.css"
api = root / "app/api/design/route.ts"

def rep(s, old, new, label):
    if old not in s:
        raise SystemExit(f"[失败] 找不到替换点：{label}")
    return s.replace(old, new, 1)

s = tsx.read_text(encoding="utf-8")

s = rep(s,
'type Material = { id: string; name: string; description: string; referenceName?: string; referenceUrl?: string; enabled?: boolean; width?: number; height?: number; unit?: "mm"|"px"; sizePreset?: string; copy?: string };',
'type Material = { id: string; name: string; description: string; referenceName?: string; referenceUrl?: string; enabled?: boolean; width?: number; height?: number; unit?: "mm"|"px"; sizePreset?: string; copy?: string; withText?: boolean };',
"Material withText")

s = rep(s,
'type DeconstructionRoute = { id:string; title:string; summary:string; rationale:string; tags:string[] };',
'''type DeconstructionRoute = { id:string; title:string; summary:string; rationale:string; tags:string[] };
type DeconstructionStudyElement = { x:number; y:number; scale:number; rotation:number; opacity:number; clip:"none"|"left"|"right"|"top"|"bottom"|"center" };
type DeconstructionStudy = { id:string; routeId:string; title:string; note:string; background:string; invert:boolean; elements:DeconstructionStudyElement[] };''',
"study types")

s = s.replace('copy:"姓名 / 职位 / 电话 / 邮箱 / 品牌信息" }','copy:"姓名 / 职位 / 电话 / 邮箱 / 品牌信息", withText:true }')
s = s.replace('copy:"品牌名 / 一句品牌短语" }','copy:"品牌名 / 一句品牌短语", withText:true }')
s = s.replace('copy:"品牌名 / 产品名 / 规格 / 辅助信息" }','copy:"品牌名 / 产品名 / 规格 / 辅助信息", withText:true }')

s = rep(s,
'  const [selectedRouteId,setSelectedRouteId]=useState<string>("");\n  const [generated,setGenerated]=useState(false);',
'  const [selectedRouteId,setSelectedRouteId]=useState<string>("");\n  const [routeStudies,setRouteStudies]=useState<Record<string,DeconstructionStudy[]>>({});\n  const [selectedStudyId,setSelectedStudyId]=useState<string>("");\n  const [generated,setGenerated]=useState(false);',
"route study state")

s = rep(s,
'setMaterials(defaultMaterials.map(x=>({...x}))); setRulesConfirmed(false); setSelectedRouteId(""); setGenerated(false);',
'setMaterials(defaultMaterials.map(x=>({...x}))); setRulesConfirmed(false); setSelectedRouteId(""); setRouteStudies({}); setSelectedStudyId(""); setGenerated(false);',
"reset studies")

s = rep(s,
'{step==="generate"&&<DeconstructionRoutes graphic={graphic} selectedRouteId={selectedRouteId} setSelectedRouteId={setSelectedRouteId} selectedExtensions={selectedExtensions} setSelectedExtensions={setSelectedExtensions}/>}',
'{step==="generate"&&<DeconstructionRoutes graphic={graphic} selectedRouteId={selectedRouteId} setSelectedRouteId={setSelectedRouteId} routeStudies={routeStudies} setRouteStudies={setRouteStudies} selectedStudyId={selectedStudyId} setSelectedStudyId={setSelectedStudyId} selectedExtensions={selectedExtensions} setSelectedExtensions={setSelectedExtensions}/>}',
"DeconstructionRoutes props")

s = rep(s,
'currentModel={currentModel} selectedRoute={routePresets.find(x=>x.id===selectedRouteId)||null}/>',
'currentModel={currentModel} selectedRoute={routePresets.find(x=>x.id===selectedRouteId)||null} selectedStudy={Object.values(routeStudies).flat().find(x=>x.id===selectedStudyId)||null}/>',
"review study prop")

a=s.index('function DeconstructionRoutes('); b=s.index('\n\nfunction Rules(',a)
new_decon = '''function StudyVisual({study,graphic}:{study:DeconstructionStudy;graphic:AssetFile|null}){
  const clip=(v:DeconstructionStudyElement["clip"])=>v==="left"?"inset(0 50% 0 0)":v==="right"?"inset(0 0 0 50%)":v==="top"?"inset(0 0 50% 0)":v==="bottom"?"inset(50% 0 0 0)":v==="center"?"inset(18% 18% 18% 18%)":"none";
  return <div className={`study-visual ${study.invert?"invert-study":""}`} style={{background:study.background||"#f2f2f2"}}>
    {study.elements.map((el,i)=>graphic?<img key={i} src={graphic.url} alt="" style={{left:`${el.x}%`,top:`${el.y}%`,width:`${Math.max(12,el.scale)}%`,transform:`translate(-50%,-50%) rotate(${el.rotation}deg)`,opacity:el.opacity,clipPath:clip(el.clip)}}/>:null)}
  </div>
}
function DeconstructionRoutes({graphic,selectedRouteId,setSelectedRouteId,routeStudies,setRouteStudies,selectedStudyId,setSelectedStudyId,selectedExtensions,setSelectedExtensions}:{graphic:AssetFile|null;selectedRouteId:string;setSelectedRouteId:(x:string)=>void;routeStudies:Record<string,DeconstructionStudy[]>;setRouteStudies:(x:Record<string,DeconstructionStudy[]>)=>void;selectedStudyId:string;setSelectedStudyId:(x:string)=>void;selectedExtensions:string[];setSelectedExtensions:(x:string[])=>void}){
  const toggle=(x:string)=>setSelectedExtensions(selectedExtensions.includes(x)?selectedExtensions.filter(v=>v!==x):[...selectedExtensions,x]);
  const [loading,setLoading]=useState(false); const [error,setError]=useState("");
  const generateStudies=async()=>{const api=readApiSettings();if(!api.key||!api.model){setError("请先到「设置」完成 AI 连接。");return;}setLoading(true);setError("");try{
    const logoImage=await svgUrlToPngDataUrl(graphic?.url);
    const r=await fetch("/api/design",{method:"POST",headers:{"Content-Type":"application/json","x-openai-key":api.key},body:JSON.stringify({mode:"deconstruct",model:api.model,provider:api.provider,baseUrl:api.baseUrl,apiMode:api.apiMode,logoImage,routes:routePresets,selectedExtensions})});
    const d=await r.json();if(!r.ok)throw new Error(d.error||"解构失败");const grouped:Record<string,DeconstructionStudy[]>={};(d.studies||[]).forEach((x:DeconstructionStudy)=>{(grouped[x.routeId]||(grouped[x.routeId]=[])).push(x)});setRouteStudies(grouped);
  }catch(e){setError(e instanceof Error?e.message:"解构失败")}finally{setLoading(false)}};
  const pick=(routeId:string,studyId?:string)=>{setSelectedRouteId(routeId);if(studyId)setSelectedStudyId(studyId)};
  return <div className="deconstruction-page"><p className="eyebrow">第 3 步 · 理解并解构 Logo</p>
    <div className="deconstruction-title-row"><div><h1>先决定这个 Logo 最值得往哪里发展。</h1><p className="muted">先让 AI 做纯图形实验，不放文案、不做 Mockup。选中的解构小样会作为第四步的视觉规则依据。</p></div><button className="primary deconstruct-ai-btn" onClick={generateStudies} disabled={loading||!graphic}>{loading?"AI 正在解构…":Object.keys(routeStudies).length?"重新生成解构":"AI 生成解构小样"}</button></div>
    {error&&<div className="api-error">{error}</div>}
    <div className="deconstruction-intro"><div className="deconstruction-logo white-preview">{graphic?<img src={graphic.url} alt="Logo"/>:<span>Logo</span>}</div><div><span className="rule-tag">当前分析原则</span><p>优先寻找：可重复单元、比例、负形、裁切、局部识别点、空间和尺度关系。</p><p>暂不处理：文字、Mockup、材质、光影、摄影氛围。</p></div></div>
    <div className="route-grid">{routePresets.map((r,i)=>{const studies=routeStudies[r.id]||[];return <div key={r.id} className={`route-card ${selectedRouteId===r.id?"selected":""}`}><button type="button" className="route-card-main" onClick={()=>pick(r.id)}><div className="route-index">0{i+1}</div><h3>{r.title}</h3><p>{r.summary}</p><small>{r.rationale}</small><div className="route-tags">{r.tags.map(t=><span key={t}>{t}</span>)}</div></button>{studies.length?<div className="route-study-grid">{studies.map(st=><button key={st.id} type="button" className={`route-study ${selectedStudyId===st.id?"selected":""}`} onClick={()=>pick(r.id,st.id)}><StudyVisual study={st} graphic={graphic}/><span>{st.title}</span><small>{st.note}</small></button>)}</div>:<div className="route-demo"><i/><i/><i/><i/></div>}<b className="route-pick-state">{selectedRouteId===r.id?(selectedStudyId&&studies.some(x=>x.id===selectedStudyId)?"已选择解构小样 ✓":"已选择方向 ✓"):"选择这个方向"}</b></div>})}</div>
    <div className="route-guidance"><span className="rule-tag">进一步约束 · 这些选项会继续作为 AI 指令</span><div className="choice-grid">{extensionOptions.map(x=><button type="button" key={x} className={selectedExtensions.includes(x)?"selected":""} onClick={()=>toggle(x)}>{selectedExtensions.includes(x)?"✓ ":"+ "}{x}</button>)}</div></div>
  </div>;
}'''
s=s[:a]+new_decon+s[b:]

a=s.index('function MaterialSetup('); b=s.index('\n\nfunction GenerateAndReview(',a)
new_ms='''function MaterialSetup({materials,onChange,compact=false}:{materials:Material[];onChange:(x:Material[])=>void;compact?:boolean}){
  const update=(id:string,p:Partial<Material>)=>onChange(materials.map(m=>m.id===id?{...m,...p}:m));
  const add=()=>onChange([...materials,{id:`custom-${Date.now()}`,name:"海报",description:"验证版式系统与信息层级。",enabled:true,width:297,height:420,unit:"mm",sizePreset:"A3 · 297 × 420 mm",copy:"品牌主张 / 标题 / 副标题 / 辅助信息",withText:true}]);
  const applyPreset=(m:Material,label:string)=>{const p=(materialPresets[m.name]||[]).find(x=>x.label===label);if(p)update(m.id,{...p,sizePreset:p.label});};
  return <section className={`material-setup ${compact?"compact":""}`}><div className="material-setup-head"><div><span className="rule-tag">{compact?"补充物料":"本轮物料与画布"}</span><h3>{compact?"新增物料不会清空已生成结果。":"先规定尺寸，再让 AI 在真实边界里做设计。"}</h3>{!compact&&<p>同一轮物料共享一套网格、字体层级、图形语法与色彩逻辑，避免每张各做各的。</p>}</div><button className="secondary" onClick={add}>+ 添加物料</button></div><div className="material-setup-grid">{materials.map((m,index)=><article className={`material-setup-card ${m.enabled===false?"off":""}`} key={m.id}><div className="material-card-top"><label><input type="checkbox" checked={m.enabled!==false} onChange={e=>update(m.id,{enabled:e.target.checked})}/><b>{String(index+1).padStart(2,"0")} · {m.name}</b></label><button className="remove-btn" onClick={()=>onChange(materials.filter(x=>x.id!==m.id))}>删除</button></div><div className="material-row"><label>物料<input value={m.name} onChange={e=>update(m.id,{name:e.target.value,sizePreset:""})}/></label><label>常用尺寸<select value={m.sizePreset||""} onChange={e=>applyPreset(m,e.target.value)}><option value="">自定义</option>{(materialPresets[m.name]||[]).map(p=><option key={p.label} value={p.label}>{p.label}</option>)}</select></label></div><div className="material-row dimensions"><label>宽<input type="number" min="1" value={m.width||0} onChange={e=>update(m.id,{width:Number(e.target.value),sizePreset:""})}/></label><span>×</span><label>高<input type="number" min="1" value={m.height||0} onChange={e=>update(m.id,{height:Number(e.target.value),sizePreset:""})}/></label><label>单位<select value={m.unit||"mm"} onChange={e=>update(m.id,{unit:e.target.value as "mm"|"px"})}><option value="mm">mm</option><option value="px">px</option></select></label></div><div className="text-mode-switch"><span>文字信息</span><button type="button" className={m.withText!==false?"selected":""} onClick={()=>update(m.id,{withText:true})}>需要文字</button><button type="button" className={m.withText===false?"selected":""} onClick={()=>update(m.id,{withText:false})}>纯图形</button></div>{m.withText!==false&&<label>必须出现的信息<textarea value={m.copy||""} onChange={e=>update(m.id,{copy:e.target.value})} placeholder="例如：品牌名 / 标题 / 副标题 / 日期 / 联系方式"/></label>}<label>设计要求<textarea value={m.description} onChange={e=>update(m.id,{description:e.target.value})} placeholder="例如：留白大、Logo 可超大裁切，但信息层级必须清晰。"/></label></article>)}</div></section>
}'''
s=s[:a]+new_ms+s[b:]

s=rep(s,'currentModel,selectedRoute}:{graphic:AssetFile|null;','currentModel,selectedRoute,selectedStudy}:{graphic:AssetFile|null;',"review selected study")
s=rep(s,'currentModel:string;selectedRoute:DeconstructionRoute|null}){','currentModel:string;selectedRoute:DeconstructionRoute|null;selectedStudy:DeconstructionStudy|null}){',"review selected study type")
s=rep(s,'materials:list.map(m=>({id:m.id,name:m.name,description:m.description,referenceName:m.referenceName})),','materials:list.map(m=>({id:m.id,name:m.name,description:m.description,referenceName:m.referenceName,width:m.width,height:m.height,unit:m.unit,copy:m.copy,withText:m.withText!==false})),',"send material config")
s=rep(s,'context:{brandColor,auxiliaryColors,ratios,selectedExtensions,selectedBoundaries,deconstructionRoute:selectedRoute},','context:{brandColor,auxiliaryColors,ratios,selectedExtensions,selectedBoundaries,deconstructionRoute:selectedRoute,deconstructionStudy:selectedStudy},',"send study")

s=rep(s,'''      if(out){
        setLayouts(Object.fromEntries(out.map(x=>[x.materialId,x])));
        setGenerated(true);
        setDeleted([]);
        setApproved([]);
      }''','''      if(out){
        setLayouts(prev=>({...prev,...Object.fromEntries(out.map(x=>[x.materialId,x]))}));
        setGenerated(true);
        setDeleted([]);
      }''',"preserve results")

s=rep(s,'  const keep=(id:string)=>setApproved(','''  const updateMaterial=(id:string,p:Partial<Material>)=>setMaterials(materials.map(m=>m.id===id?{...m,...p}:m));
  const addMaterial=()=>setMaterials([...materials,{id:`custom-${Date.now()}`,name:"海报",description:"补充验证这套视觉系统。",enabled:true,width:297,height:420,unit:"mm",sizePreset:"A3 · 297 × 420 mm",copy:"品牌主张 / 标题 / 副标题",withText:true}]);
  const generateOne=async(m:Material)=>redo(m);

  const keep=(id:string)=>setApproved(''',"material helpers")

s=rep(s,'{generated&&<div className="result-list">','''{generated&&<div className="post-generate-toolbar"><div><span className="rule-tag">继续完善系统</span><p>可以追加物料或修改尺寸，已有结果不会清空。</p></div><button className="secondary" onClick={addMaterial}>+ 补充物料</button></div>}
    {generated&&materials.filter(m=>m.enabled!==false&&!deleted.includes(m.id)&&!layouts[m.id]).map(m=><article className="pending-material-card" key={m.id}><div><b>{m.name}</b><span>新物料 · 尚未生成</span></div><div className="pending-size"><input value={m.name} onChange={e=>updateMaterial(m.id,{name:e.target.value})}/><input type="number" min="1" value={m.width||0} onChange={e=>updateMaterial(m.id,{width:Number(e.target.value)})}/><span>×</span><input type="number" min="1" value={m.height||0} onChange={e=>updateMaterial(m.id,{height:Number(e.target.value)})}/><select value={m.unit||"mm"} onChange={e=>updateMaterial(m.id,{unit:e.target.value as "mm"|"px"})}><option value="mm">mm</option><option value="px">px</option></select></div><div className="text-mode-switch"><button className={m.withText!==false?"selected":""} onClick={()=>updateMaterial(m.id,{withText:true})}>需要文字</button><button className={m.withText===false?"selected":""} onClick={()=>updateMaterial(m.id,{withText:false})}>纯图形</button></div>{m.withText!==false&&<input className="pending-copy" value={m.copy||""} onChange={e=>updateMaterial(m.id,{copy:e.target.value})} placeholder="需要出现的信息"/>}<button className="primary" onClick={()=>generateOne(m)} disabled={busy(m.id)}>{busy(m.id)?"生成中…":"生成这个物料"}</button></article>)}
    {generated&&<div className="result-list">''',"post generation add")

s=rep(s,'      {visible.map((m,i)=>{\n        const l=layouts[m.id];','      {visible.filter(m=>!!layouts[m.id]).map((m,i)=>{\n        const l=layouts[m.id];',"filter result")

s=rep(s,'''            <b>{m.name}</b>
            <span>{l?.concept||m.description||`AI 自由发挥 · ${selectedExtensions.slice(0,3).join(" / ")}`}</span>''','''            <b>{m.name}</b>
            <div className="result-size-editor"><label>W<input type="number" min="1" value={m.width||0} onChange={e=>updateMaterial(m.id,{width:Number(e.target.value)})}/></label><span>×</span><label>H<input type="number" min="1" value={m.height||0} onChange={e=>updateMaterial(m.id,{height:Number(e.target.value)})}/></label><select value={m.unit||"mm"} onChange={e=>updateMaterial(m.id,{unit:e.target.value as "mm"|"px"})}><option value="mm">mm</option><option value="px">px</option></select><div className="text-mode-switch mini"><button className={m.withText!==false?"selected":""} onClick={()=>updateMaterial(m.id,{withText:true})}>文字</button><button className={m.withText===false?"selected":""} onClick={()=>updateMaterial(m.id,{withText:false})}>纯图形</button></div></div>
            <span>{l?.concept||m.description||`AI 自由发挥 · ${selectedExtensions.slice(0,3).join(" / ")}`}</span>''',"size editor")

s=rep(s,'''      <div className={`ai-copy ${pos}`} style={{color,textAlign:layout?.textAlign||"left"}}>
        <small>{layout?.microcopy||"BRAND SYSTEM / 01"}</small>
        <strong>{layout?.headline||layout?.concept||"Identity through form."}</strong>
        <span>{layout?.subline||"A consistent visual language built from one recognizable mark."}</span>
      </div>''','''      {material.withText!==false&&<div className={`ai-copy ${pos}`} style={{color,textAlign:layout?.textAlign||"left"}}>
        <small>{layout?.microcopy||"BRAND SYSTEM / 01"}</small>
        <strong>{layout?.headline||layout?.concept||"Identity through form."}</strong>
        <span>{layout?.subline||"A consistent visual language built from one recognizable mark."}</span>
      </div>}''',"pure graphic preview")

tsx.write_text(s,encoding="utf-8")

r=api.read_text(encoding="utf-8")
schema_anchor='''const layoutItem = {
  type:"object", additionalProperties:false,
  required:["materialId","concept","backgroundColor","logoScale","logoX","logoY","logoRotation","textPosition","textColor","headline","subline","microcopy","textAlign","rationale"],
  properties:{
    materialId:{type:"string"},concept:{type:"string"},backgroundColor:{type:"string"},
    logoScale:{type:"number",minimum:0.6,maximum:5},logoX:{type:"number",minimum:-20,maximum:120},
    logoY:{type:"number",minimum:-20,maximum:120},logoRotation:{type:"number",minimum:-45,maximum:45},
    textPosition:{type:"string",enum:["top-left","top-right","bottom-left","bottom-right"]},
    textColor:{type:"string"},headline:{type:"string"},subline:{type:"string"},microcopy:{type:"string"},textAlign:{type:"string",enum:["left","center","right"]},rationale:{type:"string"}
  }
};
'''
study_schema='''const studyElement = {type:"object",additionalProperties:false,required:["x","y","scale","rotation","opacity","clip"],properties:{x:{type:"number",minimum:-20,maximum:120},y:{type:"number",minimum:-20,maximum:120},scale:{type:"number",minimum:12,maximum:180},rotation:{type:"number",minimum:-90,maximum:90},opacity:{type:"number",minimum:0.15,maximum:1},clip:{type:"string",enum:["none","left","right","top","bottom","center"]}}};
const deconstructionStudyItem = {type:"object",additionalProperties:false,required:["id","routeId","title","note","background","invert","elements"],properties:{id:{type:"string"},routeId:{type:"string"},title:{type:"string"},note:{type:"string"},background:{type:"string"},invert:{type:"boolean"},elements:{type:"array",minItems:1,maxItems:8,items:studyElement}}};
'''
if "const studyElement" not in r:r=rep(r,schema_anchor,schema_anchor+study_schema,"study schema")
r=rep(r,'const {mode,model,provider="openai",baseUrl,apiMode="responses",logoImage,materials=[],references=[],context,currentLayout,instruction}=body;','const {mode,model,provider="openai",baseUrl,apiMode="responses",logoImage,materials=[],references=[],context,currentLayout,instruction,routes=[],selectedExtensions=[]}=body;',"api body")

anchor='   return NextResponse.json({ok:true,model,provider,apiMode,status:r.status,requestUrl:url,finalUrl:r.url});\n  }\n'
block='''  if(mode==="deconstruct"){
   const schema={type:"object",additionalProperties:false,required:["studies"],properties:{studies:{type:"array",minItems:routes.length*2,maxItems:routes.length*2,items:deconstructionStudyItem}}};
   const prompt=`你是一名资深品牌图形系统设计师。只针对上传 Logo 做纯图形解构，不写文案、不做 Mockup、不增加无关新形状。每条路线生成 2 个不同实验；elements 只能是原 Logo 的复制、缩放、旋转、裁切、局部露出、重复和空间关系。geometry 强调比例/阵列，negative 强调留白/缺省，symbol 强调识别局部/重复节奏，spatial 强调超大尺度/边缘裁切。路线：${JSON.stringify(routes)}。允许延展：${JSON.stringify(selectedExtensions)}。background 只用 #FFFFFF、#111111、#E8E8E8。只返回合法 JSON。`;
   if(apiMode==="chat"){const content:any[]=[{type:"text",text:`${prompt}\\nJSON Schema：${JSON.stringify(schema)}`}];if(logoImage)content.push({type:"text",text:"原始 Logo："},{type:"image_url",image_url:{url:logoImage}});const url=`${base}/chat/completions`;const ai=await relayFetch(url,{method:"POST",headers:{"Authorization":`Bearer ${key}`,"Content-Type":"application/json"},body:JSON.stringify({model,messages:[{role:"system",content:"只输出合法 JSON，不要 Markdown。"},{role:"user",content}],temperature:0.65})});const data:any=await readResponse(ai);if(!ai.ok)return NextResponse.json({error:data?.error?.message||data?.message||data?.raw||`API 请求失败 (${ai.status})`},{status:ai.status});const text=data?.choices?.[0]?.message?.content;if(!text)return NextResponse.json({error:"模型没有返回解构结果"},{status:502});try{return NextResponse.json(extractJson(text))}catch{return NextResponse.json({error:"模型返回的解构结果不是有效 JSON"},{status:502})}}
   const content:any[]=[{type:"input_text",text:prompt}];if(logoImage)content.push({type:"input_text",text:"下面是原始 Logo："},{type:"input_image",image_url:logoImage,detail:"high"});const url=`${base}/responses`;const ai=await relayFetch(url,{method:"POST",headers:{"Authorization":`Bearer ${key}`,"Content-Type":"application/json"},body:JSON.stringify({model,store:false,input:[{role:"user",content}],text:{format:{type:"json_schema",name:"logo_deconstruction",strict:true,schema}}})});const data:any=await readResponse(ai);if(!ai.ok)return NextResponse.json({error:data?.error?.message||data?.message||data?.raw||`API 请求失败 (${ai.status})`},{status:ai.status});const text=data.output?.flatMap((x:any)=>x.content||[]).find((x:any)=>x.type==="output_text")?.text;if(!text)return NextResponse.json({error:"API 没有返回解构结果"},{status:502});return NextResponse.json(JSON.parse(text));
  }
'''
if 'if(mode==="deconstruct")' not in r:r=rep(r,anchor,anchor+block,"deconstruct mode")
r=r.replace('1. 不重新设计 Logo，不改变原始路径；从 deconstructionRoute 与 selectedExtensions 提取统一视觉语法。','1. 不重新设计 Logo，不改变原始路径；优先继承 deconstructionStudy 的尺度、裁切、重复、负形和空间关系，再结合 deconstructionRoute 与 selectedExtensions 建立统一视觉语法。')
r=r.replace('4. 不能只有 Logo。每张必须建立至少三级信息：headline、subline、microcopy；基于 material.copy 组织真实感文案，不胡编事实数据。','4. material.withText=true 时建立 headline、subline、microcopy 信息层级并基于 material.copy 组织文案；material.withText=false 时三个文字字段都返回空字符串，让纯图形系统成为主体。')
api.write_text(r,encoding="utf-8")

c=css.read_text(encoding="utf-8")
addon='''

/* v7.0 — AI deconstruction studies + expandable material system */
.deconstruction-title-row{display:flex;justify-content:space-between;gap:24px;align-items:flex-start}.deconstruct-ai-btn{flex:0 0 auto;margin-top:4px}
.route-card{padding:0!important;overflow:hidden;text-align:left}.route-card-main{display:block;width:100%;padding:16px 16px 8px;background:transparent;border:0;color:inherit;text-align:left;cursor:pointer}
.route-study-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px;padding:8px 12px 12px}.route-study{padding:0;border:1px solid var(--line);border-radius:8px;overflow:hidden;background:transparent;color:inherit;text-align:left;cursor:pointer}.route-study.selected{border-color:#27c768;box-shadow:inset 0 0 0 1px #27c768}.route-study>span,.route-study>small{display:block;padding:0 8px}.route-study>span{font-size:10px;font-weight:700;margin-top:7px}.route-study>small{font-size:8px;line-height:1.4;opacity:.6;margin:3px 0 8px}.study-visual{height:116px;position:relative;overflow:hidden}.study-visual img{position:absolute;display:block;filter:brightness(0)}.study-visual.invert-study img{filter:brightness(0) invert(1)}.route-pick-state{display:block;padding:0 16px 14px;font-size:9px;color:#27c768}
.text-mode-switch{display:flex;align-items:center;gap:6px;margin:9px 0}.text-mode-switch>span{font-size:9px;opacity:.55;margin-right:4px}.text-mode-switch button{border:1px solid var(--line);border-radius:999px;background:transparent;color:inherit;padding:5px 9px;font-size:9px}.text-mode-switch button.selected{background:#fff;color:#111;border-color:#fff}.text-mode-switch.mini{margin:0 0 0 8px}.text-mode-switch.mini button{padding:4px 7px}
.post-generate-toolbar{display:flex;justify-content:space-between;align-items:center;gap:20px;padding:12px 14px;border:1px solid var(--line);border-radius:10px;margin:10px 0}.post-generate-toolbar p{margin:4px 0 0;font-size:10px;opacity:.55}
.pending-material-card{display:grid;grid-template-columns:140px 1fr auto auto;gap:10px;align-items:center;padding:12px 14px;border:1px dashed var(--line);border-radius:10px;margin:8px 0}.pending-material-card>div:first-child{display:grid;gap:3px}.pending-material-card>div:first-child span{font-size:9px;opacity:.5}.pending-size{display:flex;align-items:center;gap:5px}.pending-size input{width:76px}.pending-size input:first-child{width:140px}.pending-size input,.pending-size select,.pending-copy{height:32px;background:transparent;color:inherit;border:1px solid var(--line);border-radius:6px;padding:0 8px}.pending-copy{width:100%;min-width:180px}
.result-card{grid-template-columns:minmax(390px,1.35fr) minmax(220px,.65fr)!important}.result-meta{padding:14px!important}.result-size-editor{display:flex;align-items:center;gap:5px;margin:8px 0}.result-size-editor label{display:flex;align-items:center;gap:4px;font-size:8px;opacity:.7}.result-size-editor input{width:64px;height:27px;background:transparent;color:inherit;border:1px solid var(--line);border-radius:5px;padding:0 6px}.result-size-editor select{height:27px;background:transparent;color:inherit;border:1px solid var(--line);border-radius:5px;padding:0 5px}.material-artboard{min-height:280px!important}
@media (max-width:900px){.deconstruction-title-row{display:block}.route-study-grid{grid-template-columns:1fr}.pending-material-card{grid-template-columns:1fr}.result-card{grid-template-columns:1fr!important}}
'''
if "v7.0 — AI deconstruction studies" not in c:c+=addon
css.write_text(c,encoding="utf-8")

print("完成：第三步 AI 解构小样 / 第四步追加物料 / 尺寸编辑 / 文字与纯图形切换 / 预览比例优化")
print("下一步运行：npm run build")
