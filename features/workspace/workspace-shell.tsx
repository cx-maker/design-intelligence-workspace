"use client";

import React, { ChangeEvent, CSSProperties, useEffect, useMemo, useRef, useState } from "react";

type WorkflowStep = "brand" | "references" | "generate" | "review" | "deliver";
type Section = "projects" | "library" | "settings";
type ProjectSummary = { id:string; name:string; step:WorkflowStep; updatedAt:number };
type AssetFile = { id: string; name: string; url: string; raw: string };
type Material = { id: string; name: string; description: string; referenceName?: string; referenceUrl?: string; enabled?: boolean; width?: number; height?: number; unit?: "mm"|"px"; sizePreset?: string; copy?: string };
type Ratios = Record<string, number>;
type DesignLayout = { materialId:string; concept:string; backgroundColor:string; logoScale:number; logoX:number; logoY:number; logoRotation:number; textPosition:"top-left"|"top-right"|"bottom-left"|"bottom-right"; textColor:string; headline:string; subline:string; microcopy:string; textAlign:"left"|"center"|"right"; rationale:string };

type ApiSettings = { provider:"openai"|"compatible"; key:string; model:string; baseUrl:string; apiMode:"responses"|"chat"; remember:boolean };
const defaultApiSettings:ApiSettings={provider:"openai",key:"",model:"",baseUrl:"",apiMode:"responses",remember:false};
function readApiSettings():ApiSettings { if(typeof window==="undefined") return defaultApiSettings; const raw=sessionStorage.getItem("diw_openai")||localStorage.getItem("diw_openai"); if(!raw) return defaultApiSettings; try{return {...defaultApiSettings,...JSON.parse(raw)}}catch{return defaultApiSettings} }
function writeApiSettings(v:ApiSettings){ if(typeof window==="undefined") return; sessionStorage.removeItem("diw_openai"); localStorage.removeItem("diw_openai"); (v.remember?localStorage:sessionStorage).setItem("diw_openai",JSON.stringify(v)); }
function clearApiSettings(){ if(typeof window==="undefined") return; sessionStorage.removeItem("diw_openai"); localStorage.removeItem("diw_openai"); }
async function imageUrlToDataUrl(url?:string){ if(!url) return undefined; const blob=await fetch(url).then(r=>r.blob()); return await new Promise<string>((resolve,reject)=>{const r=new FileReader();r.onload=()=>resolve(String(r.result));r.onerror=reject;r.readAsDataURL(blob);}); }
async function svgUrlToPngDataUrl(url?:string){ if(!url) return undefined; return await new Promise<string>((resolve,reject)=>{const img=new Image();img.onload=()=>{const c=document.createElement("canvas");c.width=1200;c.height=1200;const ctx=c.getContext("2d");if(!ctx)return reject(new Error("canvas"));ctx.fillStyle="#fff";ctx.fillRect(0,0,c.width,c.height);const scale=Math.min(900/img.width,900/img.height);const w=img.width*scale,h=img.height*scale;ctx.drawImage(img,(1200-w)/2,(1200-h)/2,w,h);resolve(c.toDataURL("image/png"));};img.onerror=reject;img.src=url;}); }

const steps: { id: WorkflowStep; label: string }[] = [
  { id: "brand", label: "导入资产" },
  { id: "references", label: "确认资产" },
  { id: "generate", label: "解构路线" },
  { id: "review", label: "平面试排" },
  { id: "deliver", label: "效果图" },
];
const defaultMaterials: Material[] = [
  { id:"card", name:"名片", description:"建立品牌最基础的信息层级与留白规则。", enabled:true, width:90, height:54, unit:"mm", sizePreset:"90 × 54 mm", copy:"姓名 / 职位 / 电话 / 邮箱 / 品牌信息" },
  { id:"bag", name:"手提袋", description:"验证大尺度 Logo、裁切、色块和短文案关系。", enabled:true, width:320, height:420, unit:"mm", sizePreset:"320 × 420 mm", copy:"品牌名 / 一句品牌短语" },
  { id:"box", name:"包装盒", description:"验证多面信息层级与系统化图形语言。", enabled:true, width:240, height:180, unit:"mm", sizePreset:"240 × 180 mm", copy:"品牌名 / 产品名 / 规格 / 辅助信息" },
];
const extensionOptions = ["等比放大", "超大裁切", "局部裁切", "完整展示", "少量重复", "图形拆解", "局部元素提取", "负形利用", "黑白反白", "允许旋转", "连续构图"];
const boundaryOptions = ["不重新设计 Logo", "不改变路径形状", "不增加无关装饰图形", "不使用光效 / 粒子 / 纹理", "不使用阴影", "不使用 3D / 透视", "不使用摄影 Mockup", "保持纯二维正视图"];
type DeconstructionRoute = { id:string; title:string; summary:string; rationale:string; tags:string[] };
const routePresets:DeconstructionRoute[] = [
  { id:"geometry", title:"几何 DNA", summary:"从 Logo 的基础几何、比例、间距和角度关系出发，建立可重复的结构语言。", rationale:"适合希望形成强识别、强系统性的平面品牌。", tags:["模块拆解","比例关系","阵列","裁切","尺度变化"] },
  { id:"negative", title:"负形 / 隐形关系", summary:"利用 Logo 中未被画出的部分、留白和脑补关系，发展更克制的辅助图形。", rationale:"适合标志本身存在隐含结构、空间错觉或正负形关系的项目。", tags:["负形","留白","缺省","局部识别","空间脑补"] },
  { id:"symbol", title:"局部符号化", summary:"抽取最有识别性的局部单元，将它发展成 pattern、icon、方向或信息图语言。", rationale:"适合需要大量物料、导视或数字界面的品牌系统。", tags:["局部提取","符号","pattern","图标","方向系统"] },
  { id:"spatial", title:"空间 / 尺度延展", summary:"保持二维 Logo 不变，但把它的角度、层级和构造理解为空间关系，用于大尺度构图。", rationale:"适合空间、建筑、零售或需要强场景感的品牌。", tags:["尺度","空间","边缘裁切","连续构图","环境应用"] },
];

function normalizeHex(x:string){ const s=x.toUpperCase(); if(/^#[0-9A-F]{6}$/.test(s)) return s; if(/^#[0-9A-F]{3}$/.test(s)) return `#${s[1]}${s[1]}${s[2]}${s[2]}${s[3]}${s[3]}`; return null; }
function extractSvgColors(raw:string){
  const matches=[...raw.matchAll(/(?:fill|stroke)=["'](#[0-9a-fA-F]{3,6})["']/g)].map(m=>normalizeHex(m[1])).filter(Boolean) as string[];
  const style=[...raw.matchAll(/(?:fill|stroke)\s*:\s*(#[0-9a-fA-F]{3,6})/g)].map(m=>normalizeHex(m[1])).filter(Boolean) as string[];
  const all=[...matches,...style].filter(x=>!['#000000','#FFFFFF'].includes(x));
  const counts=new Map<string,number>(); all.forEach(x=>counts.set(x,(counts.get(x)||0)+1));
  return [...counts.entries()].sort((a,b)=>b[1]-a[1]).map(x=>x[0]);
}
function makeAsset(file:File, raw:string):AssetFile { return {id:`${Date.now()}-${Math.random()}`,name:file.name,url:URL.createObjectURL(file),raw}; }

export function WorkspaceShell(){
  const [section,setSection]=useState<Section>("projects");
  const [started,setStarted]=useState(false);
  const [step,setStep]=useState<WorkflowStep>("brand");
  const [dark,setDark]=useState(true);
  const [projects,setProjects]=useState<ProjectSummary[]>([{id:"project-1",name:"新品牌方向",step:"brand",updatedAt:Date.now()}]);
  const [activeProjectId,setActiveProjectId]=useState("project-1");

  const [graphic,setGraphic]=useState<AssetFile|null>(null); const [cnTexts,setCnTexts]=useState<AssetFile[]>([]); const [enTexts,setEnTexts]=useState<AssetFile[]>([]);
  const [brandColor,setBrandColor]=useState("#008FDB"); const [auxiliaryColors,setAuxiliaryColors]=useState<string[]>([]); const [assetsConfirmed,setAssetsConfirmed]=useState(false);
  const [selectedExtensions,setSelectedExtensions]=useState<string[]>(["超大裁切","局部裁切","完整展示","黑白反白","图形拆解"]); const [selectedBoundaries,setSelectedBoundaries]=useState<string[]>(boundaryOptions);
  const [ratios,setRatios]=useState<Ratios>({black:20,white:45,brand:30}); const [materials,setMaterials]=useState<Material[]>(defaultMaterials); const [rulesConfirmed,setRulesConfirmed]=useState(false);
  const [selectedRouteId,setSelectedRouteId]=useState<string>("");
  const [generated,setGenerated]=useState(false); const [generating,setGenerating]=useState(false); const [approved,setApproved]=useState<string[]>([]); const [deleted,setDeleted]=useState<string[]>([]);
  const [layouts,setLayouts]=useState<Record<string,DesignLayout>>({});
  const [currentModel,setCurrentModel]=useState("");

  const activeProject=projects.find(p=>p.id===activeProjectId)||projects[0];
  useEffect(()=>{ const api=readApiSettings(); setCurrentModel(api.model||""); },[started,step,section]);
  useEffect(()=>{ if(!graphic) return; const colors=extractSvgColors(graphic.raw); if(colors.length){ setBrandColor(colors[0]); setAuxiliaryColors(colors.slice(1,5)); } },[graphic]);
  useEffect(()=>{ setProjects(prev=>prev.map(p=>p.id===activeProjectId?{...p,step,updatedAt:Date.now()}:p)); },[step,activeProjectId]);

  const resetWorkspace=()=>{
    setStep("brand"); setGraphic(null); setCnTexts([]); setEnTexts([]); setBrandColor("#008FDB"); setAuxiliaryColors([]); setAssetsConfirmed(false);
    setSelectedExtensions(["超大裁切","局部裁切","完整展示","黑白反白","图形拆解"]); setSelectedBoundaries(boundaryOptions); setRatios({black:20,white:45,brand:30});
    setMaterials(defaultMaterials.map(x=>({...x}))); setRulesConfirmed(false); setSelectedRouteId(""); setGenerated(false); setGenerating(false); setApproved([]); setDeleted([]); setLayouts({});
  };
  const createProject=(name:string)=>{
    const clean=name.trim(); if(!clean) return;
    const id=`project-${Date.now()}`;
    setProjects(prev=>[{id,name:clean,step:"brand",updatedAt:Date.now()},...prev]);
    setActiveProjectId(id);
    resetWorkspace();
    setStarted(false);
    setSection("projects");
  };
  const openCurrent=()=>{ setStep(activeProject?.step||"brand"); setStarted(true); };
  const switchProject=(id:string)=>{
    if(id===activeProjectId) return;
    const target=projects.find(p=>p.id===id); if(!target) return;
    setActiveProjectId(target.id);
    setStep(target.step);
    setSection("projects");
    setStarted(false);
  };
  const stepIndex=steps.findIndex(x=>x.id===step);
  const move=(d:1|-1)=>setStep(steps[Math.max(0,Math.min(4,stepIndex+d))].id);
  const canContinue=useMemo(()=> step==="brand"?!!graphic:step==="references"?assetsConfirmed:step==="generate"?!!selectedRouteId:step==="review"?(generated&&approved.length>0):true,[step,graphic,assetsConfirmed,selectedRouteId,generated,approved.length]);

  if(!started) return <Home section={section} setSection={setSection} dark={dark} setDark={setDark} projects={projects} activeProjectId={activeProjectId} onStart={openCurrent} onCreateProject={createProject} onSelectProject={switchProject}/>;

  return <main className={`shell ${dark?"dark":""}`}><Sidebar section={section} setSection={setSection} dark={dark} setDark={setDark} onExitWorkflow={()=>setStarted(false)}/><section className="workflow">
    <header className="topbar"><div><button className="crumb" onClick={()=>setStarted(false)}>项目</button><span> / {activeProject?.name||"当前项目"}</span></div><div className="step-count">第 {stepIndex+1} 步，共 5 步</div></header><div className="progress"><span style={{width:`${((stepIndex+1)/5)*100}%`}}/></div>
    <div className="stepper">{steps.map((x,i)=><button key={x.id} className={i<=stepIndex?"active":""} onClick={()=>i<=stepIndex&&setStep(x.id)}><i>{i+1}</i>{x.label}</button>)}</div>
    <div className="content">
      {step==="brand"&&<ImportAssets graphic={graphic} setGraphic={setGraphic} cnTexts={cnTexts} setCnTexts={setCnTexts} enTexts={enTexts} setEnTexts={setEnTexts}/>}
      {step==="references"&&<ConfirmAssets graphic={graphic} cnTexts={cnTexts} enTexts={enTexts} brandColor={brandColor} setBrandColor={setBrandColor} auxiliaryColors={auxiliaryColors} setAuxiliaryColors={setAuxiliaryColors} ratios={ratios} setRatios={setRatios} confirmed={assetsConfirmed} setConfirmed={setAssetsConfirmed}/>}
      {step==="generate"&&<DeconstructionRoutes graphic={graphic} selectedRouteId={selectedRouteId} setSelectedRouteId={setSelectedRouteId} selectedExtensions={selectedExtensions} setSelectedExtensions={setSelectedExtensions}/>}
      {step==="review"&&<GenerateAndReview graphic={graphic} brandColor={brandColor} auxiliaryColors={auxiliaryColors} ratios={ratios} selectedBoundaries={selectedBoundaries} materials={materials} setMaterials={setMaterials} layouts={layouts} setLayouts={setLayouts} selectedExtensions={selectedExtensions} approved={approved} setApproved={setApproved} deleted={deleted} setDeleted={setDeleted} generating={generating} setGenerating={setGenerating} generated={generated} setGenerated={setGenerated} currentModel={currentModel} selectedRoute={routePresets.find(x=>x.id===selectedRouteId)||null}/>}
      {step==="deliver"&&<MockupStage graphic={graphic} brandColor={brandColor} materials={materials} approved={approved} currentModel={currentModel} selectedRoute={routePresets.find(x=>x.id===selectedRouteId)||null}/>}
    </div>
    <footer className="footer">
      <button className="secondary footer-nav-button" onClick={()=>stepIndex===0?setStarted(false):move(-1)}>← 返回</button>
      <button className={`primary footer-nav-button footer-primary ${canContinue?"is-ready":""}`} disabled={!canContinue} onClick={()=>stepIndex<4&&move(1)}>{stepIndex===4?"已到导出步骤":"继续 →"}</button>
    </footer>
  </section></main>;
}

function Sidebar({section,setSection,dark,setDark,onExitWorkflow}:{section:Section;setSection:(x:Section)=>void;dark:boolean;setDark:(x:boolean)=>void;onExitWorkflow:()=>void}){ const names:Record<Section,string>={projects:"项目",library:"资料库",settings:"设置"}; const navigate=(target:Section)=>{setSection(target);onExitWorkflow();}; return <aside className="sidebar"><button type="button" className="mark mark-btn" onClick={()=>navigate("projects")}>DI</button><nav>{(["projects","library","settings"] as const).map(x=><button type="button" key={x} className={section===x?"nav-on":""} onClick={()=>navigate(x)}>{names[x]}</button>)}</nav><button type="button" className="theme-toggle" onClick={()=>setDark(!dark)}><span>{dark?"☀":"☾"}</span>{dark?"日间":"黑夜"}</button></aside>; }
function Home({section,setSection,dark,setDark,projects,activeProjectId,onStart,onCreateProject,onSelectProject}:{section:Section;setSection:(x:Section)=>void;dark:boolean;setDark:(x:boolean)=>void;projects:ProjectSummary[];activeProjectId:string;onStart:()=>void;onCreateProject:(name:string)=>void;onSelectProject:(id:string)=>void}){
  const [showNew,setShowNew]=useState(false); const [projectName,setProjectName]=useState("");
  const active=projects.find(p=>p.id===activeProjectId)||projects[0];
  const recent=projects.filter(p=>p.id!==activeProjectId).sort((a,b)=>b.updatedAt-a.updatedAt);
  const progressText=(p:ProjectSummary)=>{const i=Math.max(0,steps.findIndex(x=>x.id===p.step));return `第 ${i+1}/5 步 · ${steps[i]?.label||"导入资产"}`};
  const create=()=>{if(!projectName.trim())return;onCreateProject(projectName.trim());setProjectName("");setShowNew(false)};
  return <main className={`shell ${dark?"dark":""}`}><Sidebar section={section} setSection={setSection} dark={dark} setDark={setDark} onExitWorkflow={()=>{}}/><section className="home">
    {section==="projects"&&<>
      <p className="eyebrow">Design Intelligence Workspace</p><h1>用一个确定的 Logo，快速试出一整套品牌氛围。</h1><p className="muted home-intro">上传图形与文字资产，选择延展方式和物料，让工作台快速生成提案级二维品牌应用。</p>
      {active&&<button type="button" className="continue-card current-project-card" onClick={onStart}><div><span>当前项目</span><h2>{active.name}</h2><p>{progressText(active)}</p></div></button>}
      <div className="heading-row"><h3>最近项目</h3><button type="button" className="secondary new-project-button" onClick={()=>setShowNew(true)}>+ 新建项目</button></div>
      {recent.length?<div className="recent-projects">{recent.map(p=><button type="button" className="recent-project-card" key={p.id} onClick={()=>onSelectProject(p.id)} aria-label={`切换到项目 ${p.name}`}><span>项目</span><h4>{p.name}</h4><p>{progressText(p)}</p></button>)}</div>:<div className="empty-projects">新建项目后，之前的当前项目会移动到这里。</div>}
    </>}
    {section==="library"&&<Library/>}{section==="settings"&&<Settings/>}
    {showNew&&<div className="project-modal-backdrop" onClick={()=>setShowNew(false)}><div className="project-modal" onClick={e=>e.stopPropagation()}><span className="rule-tag">新建项目</span><h3>给这个品牌方向起个名字。</h3><input autoFocus value={projectName} onChange={e=>setProjectName(e.target.value)} onKeyDown={e=>e.key==="Enter"&&create()} placeholder="例如：唐睛方向 A"/><div><button className="secondary" onClick={()=>setShowNew(false)}>取消</button><button className="primary" disabled={!projectName.trim()} onClick={create}>新建项目</button></div></div></div>}
  </section></main>;
}

function SingleAsset({title,hint,asset,required,onChange}:{title:string;hint:string;asset:AssetFile|null;required?:boolean;onChange:(x:AssetFile)=>void}){ const ref=useRef<HTMLInputElement>(null); const load=async(e:ChangeEvent<HTMLInputElement>)=>{const f=e.target.files?.[0];if(!f)return;if(!f.name.toLowerCase().endsWith('.svg')){alert('当前版本仅支持 SVG 矢量文件。');return;}onChange(makeAsset(f,await f.text()));e.target.value='';}; return <div className="asset-upload"><input ref={ref} hidden type="file" accept=".svg,image/svg+xml" onChange={load}/><div className="asset-upload-preview white-preview">{asset?<img src={asset.url} alt=""/>:<span>SVG</span>}</div><div><div className="asset-title-row"><b>{title}</b>{required&&<em>必填</em>}</div><p>{asset?asset.name:hint}</p></div><button className="secondary" onClick={()=>ref.current?.click()}>{asset?"重新选择":"选择文件"}</button></div>; }
function MultiAssets({title,hint,assets,setAssets}:{title:string;hint:string;assets:AssetFile[];setAssets:(x:AssetFile[])=>void}){ const ref=useRef<HTMLInputElement>(null); const load=async(e:ChangeEvent<HTMLInputElement>)=>{const files=[...(e.target.files||[])]; const valid=files.filter(f=>f.name.toLowerCase().endsWith('.svg')); const loaded=await Promise.all(valid.map(async f=>makeAsset(f,await f.text()))); setAssets([...assets,...loaded]);e.target.value='';}; return <div className="multi-upload"><div className="multi-upload-head"><div><b>{title}</b><p>{hint}</p></div><button className="secondary" onClick={()=>ref.current?.click()}>+ 添加版式</button><input ref={ref} hidden multiple type="file" accept=".svg,image/svg+xml" onChange={load}/></div>{assets.length?<div className="variant-grid">{assets.map((a,i)=><div className="variant-card" key={a.id}><div className="white-preview"><img src={a.url} alt=""/></div><span>版式 {i+1}</span><small>{a.name}</small><button onClick={()=>setAssets(assets.filter(x=>x.id!==a.id))}>删除</button></div>)}</div>:<div className="variant-empty">尚未提供，可跳过。</div>}</div>; }
function ImportAssets({graphic,setGraphic,cnTexts,setCnTexts,enTexts,setEnTexts}:{graphic:AssetFile|null;setGraphic:(x:AssetFile)=>void;cnTexts:AssetFile[];setCnTexts:(x:AssetFile[])=>void;enTexts:AssetFile[];setEnTexts:(x:AssetFile[])=>void}){ return <div className="single wide-single"><p className="eyebrow">第 1 步 · 导入资产</p><h1>先把 Logo 图形和文字版式交给工作台。</h1><p className="muted">Logo 图形必填；中文和英文可以各自上传多个既定版式，例如单行、两行。每一个版式都会成为后续 AI 可调用的品牌资产。</p><div className="asset-upload-stack"><SingleAsset title="Logo 图形" hint="上传定稿图形主体 SVG" required asset={graphic} onChange={setGraphic}/><MultiAssets title="中文文字版式" hint="可选 · 支持多个版式" assets={cnTexts} setAssets={setCnTexts}/><MultiAssets title="英文文字版式" hint="可选 · 支持多个版式" assets={enTexts} setAssets={setEnTexts}/></div></div>; }

function PreviewCard({title,asset}:{title:string;asset:AssetFile|null}){return <div className="asset-preview-card"><span>{title}</span><div className="white-preview">{asset?<img src={asset.url} alt=""/>:<small>未提供</small>}</div><b>{asset?.name||"—"}</b></div>}
function VariantPreview({title,assets}:{title:string;assets:AssetFile[]}){return <div className="asset-preview-card multi-preview"><span>{title}</span><div className="preview-variants">{assets.length?assets.map((a,i)=><div className="white-preview" key={a.id}><img src={a.url} alt=""/><small>{i+1}</small></div>):<div className="white-preview"><small>未提供</small></div>}</div><b>{assets.length?`${assets.length} 个可用版式`:"—"}</b></div>}
function ColorEditor({color,onChange,onRemove,locked}:{color:string;onChange:(x:string)=>void;onRemove?:()=>void;locked?:boolean}){return <div className="color-editor"><input type="color" value={color} onChange={e=>onChange(e.target.value.toUpperCase())}/><input value={color} onChange={e=>{const x=e.target.value.toUpperCase();if(/^#[0-9A-F]{0,6}$/.test(x))onChange(x)}}/>{!locked&&onRemove&&<button onClick={onRemove}>×</button>}</div>}
function ConfirmAssets({graphic,cnTexts,enTexts,brandColor,setBrandColor,auxiliaryColors,setAuxiliaryColors,ratios,setRatios,confirmed,setConfirmed}:{graphic:AssetFile|null;cnTexts:AssetFile[];enTexts:AssetFile[];brandColor:string;setBrandColor:(x:string)=>void;auxiliaryColors:string[];setAuxiliaryColors:(x:string[])=>void;ratios:Ratios;setRatios:(x:Ratios)=>void;confirmed:boolean;setConfirmed:(x:boolean)=>void}){ const addAux=()=>setAuxiliaryColors([...auxiliaryColors,"#B8B8B8"]); return <div className="single wide-single"><p className="eyebrow">第 2 步 · 确认资产</p><h1>确认后面允许使用的品牌原料。</h1><p className="muted">工作台会先从 Logo SVG 中读取颜色作为建议值；你仍然可以手动修改主色，并添加多个辅助色。</p><div className="asset-confirm-grid"><PreviewCard title="Logo 图形" asset={graphic}/><VariantPreview title="中文版式" assets={cnTexts}/><VariantPreview title="英文版式" assets={enTexts}/></div><section className="color-panel"><div className="color-panel-head"><div><span>品牌主色</span><small>已尝试从 Logo SVG 自动识别</small></div></div><ColorEditor color={brandColor} onChange={setBrandColor} locked/><div className="color-panel-head aux-head"><div><span>辅助色</span><small>可多选 · 后续作为 AI 可调用色板</small></div><button className="secondary" onClick={addAux}>+ 添加辅助色</button></div><div className="aux-list">{auxiliaryColors.length?auxiliaryColors.map((c,i)=><ColorEditor key={`${c}-${i}`} color={c} onChange={x=>setAuxiliaryColors(auxiliaryColors.map((v,j)=>j===i?x:v))} onRemove={()=>setAuxiliaryColors(auxiliaryColors.filter((_,j)=>j!==i))}/>):<small>未识别到其它颜色，可按需添加。</small>}</div></section><section className="color-panel ratio-panel-step2"><div className="color-panel-head"><div><span>颜色使用比例</span><small>把色板进一步变成系统规则，而不是让 AI 随机配色。</small></div></div><ColorRatio ratios={ratios} setRatios={setRatios} brandColor={brandColor} auxiliaryColors={auxiliaryColors}/></section><label className="confirm-check"><input type="checkbox" checked={confirmed} onChange={e=>setConfirmed(e.target.checked)}/><span>确认：后续 AI 只使用上述 Logo、文字版式与色板，不重新设计 Logo。</span></label></div>; }

function ToggleChips({options,selected,setSelected}:{options:string[];selected:string[];setSelected:(x:string[])=>void}){const toggle=(x:string)=>setSelected(selected.includes(x)?selected.filter(y=>y!==x):[...selected,x]);return <div className="choice-grid">{options.map(x=><button key={x} className={selected.includes(x)?"selected":""} onClick={()=>toggle(x)}>{selected.includes(x)?"✓ ":"+ "}{x}</button>)}</div>}
function ColorRatio({ratios,setRatios,brandColor,auxiliaryColors}:{ratios:Ratios;setRatios:(x:Ratios)=>void;brandColor:string;auxiliaryColors:string[]}){
  const entries=[
    {key:"black",label:"黑色",color:"#111111",defaultValue:20},
    {key:"white",label:"白色",color:"#FFFFFF",defaultValue:45},
    {key:"brand",label:"品牌主色",color:brandColor,defaultValue:30},
    ...auxiliaryColors.map((color,index)=>({key:`aux-${index}`,label:`辅助色 ${index+1}`,color,defaultValue:5}))
  ];
  useEffect(()=>{
    const next={...ratios}; let changed=false;
    entries.forEach(item=>{if(next[item.key]===undefined){next[item.key]=item.defaultValue;changed=true;}});
    Object.keys(next).forEach(key=>{if(key.startsWith("aux-")&&!entries.some(item=>item.key===key)){delete next[key];changed=true;}});
    if(changed)setRatios(next);
  },[brandColor,auxiliaryColors.join("|")]);
  const total=entries.reduce((sum,item)=>sum+(ratios[item.key]??item.defaultValue),0)||1;
  const update=(key:string,value:number)=>setRatios({...ratios,[key]:value});
  return <div><div className="ratio-bar">{entries.map(item=><i key={item.key} title={`${item.label} ${ratios[item.key]??item.defaultValue}%`} style={{width:`${((ratios[item.key]??item.defaultValue)/total)*100}%`,background:item.color}}/>)}</div><div className="ratio-controls">{entries.map(item=><label key={item.key}><span><i style={{background:item.color}}/>{item.label}<b>{ratios[item.key]??item.defaultValue}%</b></span><input type="range" min="0" max="100" value={ratios[item.key]??item.defaultValue} onChange={e=>update(item.key,Number(e.target.value))}/></label>)}</div><p>黑白作为基础色默认保留；主色与所有辅助色来自上一步确认的品牌色板。这里的比例会作为 AI 的配色权重指令。</p></div>
}

function DeconstructionRoutes({graphic,selectedRouteId,setSelectedRouteId,selectedExtensions,setSelectedExtensions}:{graphic:AssetFile|null;selectedRouteId:string;setSelectedRouteId:(x:string)=>void;selectedExtensions:string[];setSelectedExtensions:(x:string[])=>void}){
  const toggle=(x:string)=>setSelectedExtensions(selectedExtensions.includes(x)?selectedExtensions.filter(v=>v!==x):[...selectedExtensions,x]);
  return <div className="deconstruction-page">
    <p className="eyebrow">第 3 步 · 理解并解构 Logo</p>
    <h1>先决定这个 Logo 最值得往哪里发展。</h1>
    <p className="muted">这里不做物料。工作台先理解图形结构，再给出几条可延展路线。你只选一条最有潜力的，后面的平面系统都沿这条路线执行。</p>
    <div className="deconstruction-intro">
      <div className="deconstruction-logo white-preview">{graphic?<img src={graphic.url} alt="Logo"/>:<span>Logo</span>}</div>
      <div>
        <span className="rule-tag">当前分析原则</span>
        <p>优先寻找：可重复的几何单元、独特比例、负形关系、局部识别点、尺度与空间潜力。</p>
        <p>暂不处理：Mockup、材质、光影、摄影氛围。</p>
      </div>
    </div>

    <div className="route-grid">
      {routePresets.map((r,i)=><button type="button" key={r.id} className={`route-card ${selectedRouteId===r.id?"selected":""}`} onClick={()=>setSelectedRouteId(r.id)}>
        <div className="route-index">0{i+1}</div>
        <div className="route-demo">
          <i/><i/><i/><i/>
        </div>
        <h3>{r.title}</h3>
        <p>{r.summary}</p>
        <small>{r.rationale}</small>
        <div className="route-tags">{r.tags.map(t=><span key={t}>{t}</span>)}</div>
        <b>{selectedRouteId===r.id?"已选择 ✓":"选择这个方向"}</b>
      </button>)}
    </div>

    <div className="route-guidance">
      <span className="rule-tag">进一步约束 · 这些选项会继续作为 AI 指令</span>
      <div className="choice-grid">
        {extensionOptions.map(x=><button type="button" key={x} className={selectedExtensions.includes(x)?"selected":""} onClick={()=>toggle(x)}>{selectedExtensions.includes(x)?"✓ ":"+ "}{x}</button>)}
      </div>
    </div>
  </div>;
}

function Rules({selectedExtensions,setSelectedExtensions,selectedBoundaries,setSelectedBoundaries,ratios,setRatios,brandColor,auxiliaryColors,materials,setMaterials,confirmed,setConfirmed}:{selectedExtensions:string[];setSelectedExtensions:(x:string[])=>void;selectedBoundaries:string[];setSelectedBoundaries:(x:string[])=>void;ratios:Ratios;setRatios:(x:Ratios)=>void;brandColor:string;auxiliaryColors:string[];materials:Material[];setMaterials:(x:Material[])=>void;confirmed:boolean;setConfirmed:(x:boolean)=>void}){ const update=(id:string,p:Partial<Material>)=>setMaterials(materials.map(m=>m.id===id?{...m,...p}:m)); const add=()=>setMaterials([...materials,{id:`custom-${Date.now()}`,name:"新物料",description:""}]); const refInput=(id:string,e:ChangeEvent<HTMLInputElement>)=>{const f=e.target.files?.[0];if(f)update(id,{referenceName:f.name,referenceUrl:URL.createObjectURL(f)})}; return <div className="rules-page"><p className="eyebrow">第 3 步 · 延展规则</p><h1>把你的判断变成 AI 的设计指令。</h1><p className="muted">前端只是把复杂 Prompt 变成简单选择题；真正生成时，所有选项、比例、描述和参考图都会一起进入 AI 指令。</p><section className="rule-card"><span className="rule-tag">Logo 延展方式 · 多选</span><ToggleChips options={extensionOptions} selected={selectedExtensions} setSelected={setSelectedExtensions}/></section><section className="rule-card"><span className="rule-tag">颜色使用倾向</span><ColorRatio ratios={ratios} setRatios={setRatios} brandColor={brandColor} auxiliaryColors={auxiliaryColors}/></section><section className="rule-card"><span className="rule-tag">视觉边界 · 多选</span><ToggleChips options={boundaryOptions} selected={selectedBoundaries} setSelected={setSelectedBoundaries}/></section><section className="rule-card"><div className="rule-head"><div><span className="rule-tag">首轮物料</span><h3>告诉 AI 这次要做什么。</h3></div><button className="secondary" onClick={add}>+ 新增物料</button></div><div className="material-editor-list">{materials.map((m,index)=><div className="material-editor" key={m.id}><div className="material-number">{String(index+1).padStart(2,"0")}</div><div className="material-fields"><input value={m.name} onChange={e=>update(m.id,{name:e.target.value})}/><textarea value={m.description} onChange={e=>update(m.id,{description:e.target.value})} placeholder="设计描述（选填）。没有描述时由 AI 自由发挥。"/><label className="reference-upload"><input type="file" accept="image/*" hidden onChange={e=>refInput(m.id,e)}/>{m.referenceUrl?<><img src={m.referenceUrl} alt="参考图"/><span>更换参考图</span></>:<span>+ 上传参考图（选填）</span>}</label>{m.referenceName&&<small className="reference-name">{m.referenceName}</small>}</div><button className="remove-btn" onClick={()=>setMaterials(materials.filter(x=>x.id!==m.id))}>删除</button></div>)}</div></section><label className="confirm-check"><input type="checkbox" checked={confirmed} onChange={e=>setConfirmed(e.target.checked)}/><span>使用以上选择作为本轮 AI 生成指令。</span></label></div>; }


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

function GenerateAndReview({graphic,brandColor,auxiliaryColors,ratios,selectedBoundaries,materials,setMaterials,layouts,setLayouts,selectedExtensions,approved,setApproved,deleted,setDeleted,generating,setGenerating,generated,setGenerated,currentModel,selectedRoute}:{graphic:AssetFile|null;brandColor:string;auxiliaryColors:string[];ratios:Ratios;selectedBoundaries:string[];materials:Material[];setMaterials:(x:Material[])=>void;layouts:Record<string,DesignLayout>;setLayouts:React.Dispatch<React.SetStateAction<Record<string,DesignLayout>>>;selectedExtensions:string[];approved:string[];setApproved:(x:string[])=>void;deleted:string[];setDeleted:(x:string[])=>void;generating:boolean;setGenerating:(x:boolean)=>void;generated:boolean;setGenerated:(x:boolean)=>void;currentModel:string;selectedRoute:DeconstructionRoute|null}){
  const [editing,setEditing]=useState<Material|null>(null);
  const [copyEditing,setCopyEditing]=useState<Material|null>(null);
  const [copyDraft,setCopyDraft]=useState({headline:"",subline:"",microcopy:""});
  const [adjustText,setAdjustText]=useState("");
  const [error,setError]=useState("");
  const [loadingIds,setLoadingIds]=useState<string[]>([]);
  const visible=materials.filter(m=>m.enabled!==false&&!deleted.includes(m.id));
  const busy=(id:string)=>loadingIds.includes(id);

  const callAi=async(mode:"generate"|"adjust",target?:Material,instruction?:string)=>{
    const api=readApiSettings();
    if(!api.key||!api.model){
      setError("还没有完成 AI API 配置。请先到左侧「设置」填写 Key 和模型并测试连接。");
      return null;
    }
    const logoImage=await svgUrlToPngDataUrl(graphic?.url);
    const list=target?[target]:visible;
    const refs=await Promise.all(list.map(async m=>({id:m.id,image:await imageUrlToDataUrl(m.referenceUrl)})));
    const res=await fetch('/api/design',{
      method:'POST',
      headers:{'Content-Type':'application/json','x-openai-key':api.key},
      body:JSON.stringify({
        mode,model:api.model,provider:api.provider,baseUrl:api.baseUrl,apiMode:api.apiMode,
        logoImage,
        materials:list.map(m=>({id:m.id,name:m.name,description:m.description,referenceName:m.referenceName})),
        references:refs,
        context:{brandColor,auxiliaryColors,ratios,selectedExtensions,selectedBoundaries,deconstructionRoute:selectedRoute},
        currentLayout:target?layouts[target.id]:undefined,
        instruction
      })
    });
    const data=await res.json();
    if(!res.ok) throw new Error(data.error||'AI 请求失败');
    return data.layouts as DesignLayout[];
  };

  const generate=async()=>{
    setError("");
    setGenerating(true);
    try{
      const out=await callAi('generate');
      if(out){
        setLayouts(Object.fromEntries(out.map(x=>[x.materialId,x])));
        setGenerated(true);
        setDeleted([]);
        setApproved([]);
      }
    }catch(e){
      setError(e instanceof Error?e.message:'生成失败');
    }finally{
      setGenerating(false);
    }
  };

  const redo=async(m:Material)=>{
    if(busy(m.id)) return;
    setError("");
    setLoadingIds(prev=>[...prev,m.id]);
    try{
      const out=await callAi('generate',m);
      if(out?.[0]) setLayouts(prev=>({...prev,[m.id]:out[0]}));
    }catch(e){
      setError(e instanceof Error?e.message:'重做失败');
    }finally{
      setLoadingIds(prev=>prev.filter(id=>id!==m.id));
    }
  };

  const adjust=async()=>{
    if(!editing||!adjustText.trim()) return;
    const target=editing;
    const instruction=adjustText.trim();
    setError("");
    setEditing(null);
    setAdjustText("");
    setLoadingIds(prev=>prev.includes(target.id)?prev:[...prev,target.id]);
    try{
      const out=await callAi('adjust',target,instruction);
      if(out?.[0]) setLayouts(prev=>({...prev,[target.id]:out[0]}));
    }catch(e){
      setError(e instanceof Error?e.message:'调整失败');
    }finally{
      setLoadingIds(prev=>prev.filter(id=>id!==target.id));
    }
  };

  const keep=(id:string)=>setApproved(approved.includes(id)?approved.filter(x=>x!==id):[...approved,id]);
  const remove=(id:string)=>{
    if(busy(id)) return;
    setDeleted([...deleted,id]);
    setApproved(approved.filter(x=>x!==id));
  };

  return <div className="review-page">
    <p className="eyebrow">第 4 步 · 平面矢量试排</p>
    <div className="review-heading-row">
      <div>
        <h1>{generated?"先判断平面系统是否成立。":"选几个物料，验证这条视觉路线。"}</h1>
        <p className="muted">这一层只看二维正视图、比例、留白、图形关系和信息层级。效果图留到下一步。</p>
      </div>
      <div className="review-badges"><div className="model-badge"><span>当前模型</span><b>{currentModel||"未配置"}</b></div><div className="model-badge"><span>当前路线</span><b>{selectedRoute?.title||"未选择"}</b></div></div>
    </div>

    {error&&<div className="api-error">{error}</div>}

    {!generated&&<MaterialSetup materials={materials} onChange={setMaterials}/>}

    {!generated&&<button className="primary large generate-btn" onClick={generate} disabled={generating}>
      {generating?"AI 正在试排…":"生成平面试排"}
    </button>}

    {generated&&<div className="result-list">
      {visible.map((m,i)=>{
        const l=layouts[m.id];
        const isBusy=busy(m.id);
        return <article className={`result-card ${isBusy?"is-generating":""}`} key={m.id}>
          <div className="preview-loading-wrap">
            <DesignPreview layout={l} graphic={graphic} material={m} fallbackIndex={i}/>
            {isBusy&&<div className="preview-sweep" aria-label="AI 正在生成"><span>AI 正在调整…</span></div>}
          </div>
          <div className="result-meta">
            <b>{m.name}</b>
            <span>{l?.concept||m.description||`AI 自由发挥 · ${selectedExtensions.slice(0,3).join(" / ")}`}</span>
            {l?.rationale&&<small className="ai-rationale">{l.rationale}</small>}
            <div>
              <button className={approved.includes(m.id)?"approved":""} onClick={()=>keep(m.id)} disabled={isBusy}>
                {approved.includes(m.id)?"已保留 ✓":"保留"}
              </button>
              <button onClick={()=>{setEditing(m);setAdjustText("")}} disabled={isBusy}>调整</button>
              <button onClick={()=>{const x=layouts[m.id];setCopyEditing(m);setCopyDraft({headline:x?.headline||"",subline:x?.subline||"",microcopy:x?.microcopy||""})}} disabled={isBusy}>文字</button>
              <button onClick={()=>redo(m)} disabled={isBusy}>{isBusy?"生成中…":"重做"}</button>
              <button className="danger-btn" onClick={()=>remove(m.id)} disabled={isBusy}>删除</button>
            </div>
          </div>
        </article>
      })}
    </div>}

    {editing&&<div className="adjust-overlay" onClick={()=>setEditing(null)}>
      <div className="adjust-panel" onClick={e=>e.stopPropagation()}>
        <span className="rule-tag">局部调整 · {editing.name}</span>
        <h3>告诉 AI 只改哪里。</h3>
        <p>提交后窗口会立即关闭，当前预览会扫光等待新结果；其它方案仍可继续浏览。</p>
        <div className="quick-adjust">
          {["Logo 再大一点","留白更多","改成白底","文字更靠边","保持构图，只调整比例"].map(x=>
            <button key={x} onClick={()=>setAdjustText(x)}>{x}</button>
          )}
        </div>
        <textarea autoFocus value={adjustText} onChange={e=>setAdjustText(e.target.value)}
          placeholder="例如：保持整体构图，只把 Logo 放大 20%，并让左下角留白更多。"/>
        <div className="adjust-actions">
          <button className="secondary" onClick={()=>setEditing(null)}>取消</button>
          <button className="primary" onClick={adjust} disabled={!adjustText.trim()}>应用调整</button>
        </div>
      </div>
    </div>}

    {copyEditing&&<div className="adjust-overlay" onClick={()=>setCopyEditing(null)}>
      <div className="adjust-panel copy-panel" onClick={e=>e.stopPropagation()}>
        <span className="rule-tag">文字信息 · {copyEditing.name}</span>
        <h3>直接修改这张平面里的文字。</h3>
        <p>这里只改文字，不重新调用 AI，也不改变 Logo、网格和版式结构。</p>
        <label>主标题<input value={copyDraft.headline} onChange={e=>setCopyDraft({...copyDraft,headline:e.target.value})}/></label>
        <label>副信息<textarea value={copyDraft.subline} onChange={e=>setCopyDraft({...copyDraft,subline:e.target.value})}/></label>
        <label>微型信息<input value={copyDraft.microcopy} onChange={e=>setCopyDraft({...copyDraft,microcopy:e.target.value})}/></label>
        <div className="adjust-actions">
          <button className="secondary" onClick={()=>setCopyEditing(null)}>取消</button>
          <button className="primary" onClick={()=>{
            const old=layouts[copyEditing.id];
            if(old) setLayouts(prev=>({...prev,[copyEditing.id]:{...old,...copyDraft}}));
            setCopyEditing(null);
          }}>保存文字</button>
        </div>
      </div>
    </div>}
  </div>;
}
function DesignPreview({layout,graphic,material,fallbackIndex}:{layout?:DesignLayout;graphic:AssetFile|null;material:Material;fallbackIndex:number}){
  const bg=layout?.backgroundColor||(fallbackIndex%3===0?'#111111':fallbackIndex%3===1?'#FFFFFF':'#008FDB');
  const pos=layout?.textPosition||'bottom-left';
  const color=layout?.textColor||(bg==='#FFFFFF'?'#111111':'#FFFFFF');
  const w=Math.max(1,material.width||90);
  const h=Math.max(1,material.height||54);
  const ratio=w/h;
  const planeStyle:CSSProperties = ratio>=1
    ? {width:"76%",aspectRatio:`${w}/${h}`,maxHeight:"82%"}
    : {height:"82%",aspectRatio:`${w}/${h}`,maxWidth:"76%"};

  return <div className="material-artboard">
    <div className="material-plane ai-design-preview" style={{...planeStyle,background:bg}}>
      {graphic&&<img className="ai-logo" src={graphic.url} alt="" style={{
        left:`${layout?.logoX??65}%`,
        top:`${layout?.logoY??45}%`,
        width:`${Math.max(20,(layout?.logoScale??2)*28)}%`,
        transform:`translate(-50%,-50%) rotate(${layout?.logoRotation??0}deg)`
      }}/>}
      <div className={`ai-copy ${pos}`} style={{color,textAlign:layout?.textAlign||"left"}}>
        <small>{layout?.microcopy||"BRAND SYSTEM / 01"}</small>
        <strong>{layout?.headline||layout?.concept||"Identity through form."}</strong>
        <span>{layout?.subline||"A consistent visual language built from one recognizable mark."}</span>
      </div>
      <em className="material-size-tag">{w} × {h} {material.unit||"mm"}</em>
    </div>
  </div>
}



function MockupStage({graphic,brandColor,materials,approved,currentModel,selectedRoute}:{graphic:AssetFile|null;brandColor:string;materials:Material[];approved:string[];currentModel:string;selectedRoute:DeconstructionRoute|null}){
  const kept=materials.filter(m=>approved.includes(m.id));
  const [scene,setScene]=useState<Record<string,string>>({});
  const [loading,setLoading]=useState<string[]>([]);
  const generate=(id:string)=>{
    if(loading.includes(id))return;
    setLoading(x=>[...x,id]);
    window.setTimeout(()=>{
      setScene(prev=>({...prev,[id]:"ready"}));
      setLoading(x=>x.filter(v=>v!==id));
    },1200);
  };
  return <div className="mockup-page">
    <p className="eyebrow">第 5 步 · 效果图</p>
    <h1>平面确定后，再把它放进真实世界。</h1>
    <p className="muted">这里只使用第四步明确保留的平面方案。后续接图像模型时，会把平面设计作为硬约束，把参考图只当作场景、材质、构图和光线参考。</p>
    <div className="mockup-context">
      <div><span>视觉路线</span><b>{selectedRoute?.title||"—"}</b></div>
      <div><span>当前模型</span><b>{currentModel||"—"}</b></div>
      <div><span>保留方案</span><b>{kept.length} 个</b></div>
    </div>
    {kept.length===0?<div className="empty-projects">先回到第四步，至少保留一个平面方案。</div>:
    <div className="mockup-list">{kept.map((m,i)=>{
      const busy=loading.includes(m.id); const ready=scene[m.id]==="ready";
      return <article className="mockup-card" key={m.id}>
        <div className={`mockup-preview ${ready?"ready":""}`}>
          <div className="mockup-plane" style={{background:i%2?brandColor:"#f3f3f0"}}>
            {graphic&&<img src={graphic.url} alt="Logo"/>}<small>{m.name}</small>
          </div>
          {busy&&<div className="preview-sweep"><span>正在生成效果图…</span></div>}
          {!ready&&!busy&&<div className="mockup-placeholder">平面方案已锁定<br/>等待生成场景</div>}
          {ready&&<div className="mockup-scene-label">效果图占位 · 下一轮接图像模型</div>}
        </div>
        <div className="mockup-meta">
          <h3>{m.name}</h3>
          <p>参考图将决定场景、镜头、材质和氛围；Logo 与平面结构保持不变。</p>
          <label className="reference-upload"><span>+ 上传效果图参考（下一轮接入）</span></label>
          <button className="primary" onClick={()=>generate(m.id)} disabled={busy}>{busy?"生成中…":ready?"重新生成效果图":"生成效果图"}</button>
        </div>
      </article>
    })}</div>}
  </div>;
}


function Library(){return <><p className="eyebrow">资料库</p><h1>参考与历史资产。</h1><p className="muted">后续保存 Logo、文字版式、色板、参考图和成功规则。</p><div className="empty-projects">当前还没有保存的资料。</div></>}
function Settings(){
  const [provider,setProvider]=useState<"openai"|"compatible">("openai");
  const [key,setKey]=useState(""); const [model,setModel]=useState(""); const [baseUrl,setBaseUrl]=useState("");
  const [apiMode,setApiMode]=useState<"responses"|"chat">("responses"); const [remember,setRemember]=useState(false);
  const [verified,setVerified]=useState(false); const [testing,setTesting]=useState(false); const [message,setMessage]=useState("");
  useEffect(()=>{const v=readApiSettings();setProvider(v.provider);setKey(v.key);setModel(v.model);setBaseUrl(v.baseUrl);setApiMode(v.apiMode);setRemember(v.remember);setVerified(false)},[]);
  const current=():ApiSettings=>({provider,key:key.trim(),model:model.trim(),baseUrl:baseUrl.trim(),apiMode,remember});
  const save=()=>{if(!key.trim()||!model.trim())return;writeApiSettings(current());setVerified(false);setMessage("配置已保存，建议先测试连接")};
  const test=async()=>{
    if(!key.trim()||!model.trim()){setMessage("请先填写 API Key 和模型名");return;}
    if(provider==="compatible"&&!baseUrl.trim()){setMessage("请填写中转 API Base URL");return;}
    setTesting(true);setVerified(false);setMessage("");
    try{
      const r=await fetch('/api/design',{method:'POST',headers:{'Content-Type':'application/json','x-openai-key':key.trim()},body:JSON.stringify({mode:'test',model:model.trim(),provider,baseUrl:baseUrl.trim(),apiMode})});
      const d=await r.json();if(!r.ok)throw new Error(d.error||'连接失败');
      writeApiSettings(current());setVerified(true);setMessage(`连接成功 · ${model.trim()} · ${apiMode==="responses"?"Responses":"Chat Completions"}`);
    }catch(e){setMessage(e instanceof Error?e.message:'连接失败')}finally{setTesting(false)}
  };
  const clear=()=>{clearApiSettings();setKey("");setModel("");setBaseUrl("");setVerified(false);setMessage("已断开")};
  const changeProvider=(p:"openai"|"compatible")=>{setProvider(p);setVerified(false);setMessage("");if(p==="openai"){setBaseUrl("");setApiMode("responses")}else{setApiMode("chat")}};
  return <><p className="eyebrow">设置</p><h1>AI 连接。</h1><p className="muted">使用自己的 API。可以直连 OpenAI，也可以连接兼容 OpenAI 协议的第三方中转。</p><div className="api-settings"><div className="api-status"><i className={verified?"on":""}/><div><b>{verified?"AI 已连接":"尚未验证连接"}</b><span>{verified?"现在可以在第 4 步真实生成":"保存配置不等于连接成功，请先测试"}</span></div></div><div className="provider-switch"><button className={provider==="openai"?"selected":""} onClick={()=>changeProvider("openai")}>OpenAI 官方</button><button className={provider==="compatible"?"selected":""} onClick={()=>changeProvider("compatible")}>OpenAI 兼容中转</button></div>{provider==="compatible"&&<label><span>API Base URL</span><input value={baseUrl} onChange={e=>{setBaseUrl(e.target.value);setVerified(false)}} placeholder="https://example.com/v1"/></label>}<label><span>API Key</span><input type="password" value={key} onChange={e=>{setKey(e.target.value);setVerified(false)}} placeholder="sk-… / 中转平台 Key" autoComplete="off"/></label><label><span>模型名</span><input value={model} onChange={e=>{setModel(e.target.value);setVerified(false)}} placeholder={provider==="openai"?"填写你的 API 可用模型 ID":"按中转平台提供的模型名填写"}/></label><label><span>接口模式</span><select value={apiMode} onChange={e=>{setApiMode(e.target.value as "responses"|"chat");setVerified(false)}}><option value="responses">Responses API</option><option value="chat">Chat Completions</option></select></label><label className="remember-key"><input type="checkbox" checked={remember} onChange={e=>setRemember(e.target.checked)}/><span>记住在这台设备上</span></label><div className="api-setting-actions"><button className="secondary" onClick={test} disabled={testing||!key.trim()||!model.trim()}>{testing?"测试中…":"测试连接"}</button><button className="primary" onClick={save} disabled={!key.trim()||!model.trim()}>保存配置</button>{key&&<button className="secondary" onClick={clear}>断开</button>}</div>{message&&<div className="api-message">{message}</div>}{provider==="compatible"?<small className="relay-warning">第三方中转服务会接触你提交的提示词、Logo 预览和参考图。请只使用你信任的服务商；本工具不会验证或担保第三方服务的数据安全。</small>:<small>Key 只保存在当前浏览器会话，或在你勾选后保存在本机浏览器。生成请求会经你的 Vercel 服务端临时转发。</small>}</div></>
}
