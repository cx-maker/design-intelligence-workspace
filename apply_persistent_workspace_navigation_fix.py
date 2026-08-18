from pathlib import Path

root = Path.cwd()
tsx = root / "features/workspace/workspace-shell.tsx"
css = root / "features/workspace/workspace-shell.css"

def rep(s, old, new, label):
    if old not in s:
        raise SystemExit(f"[失败] 找不到替换点：{label}")
    return s.replace(old, new, 1)

s = tsx.read_text(encoding="utf-8")

s = rep(
    s,
    'type ApiSettings = { provider:"openai"|"compatible"; key:string; model:string; baseUrl:string; apiMode:"responses"|"chat"; remember:boolean };',
    'type ApiSettings = { provider:"openai"|"compatible"; key:string; model:string; baseUrl:string; apiMode:"responses"|"chat"; remember:boolean; verified?:boolean };',
    "ApiSettings verified"
)
s = rep(
    s,
    'const defaultApiSettings:ApiSettings={provider:"openai",key:"",model:"",baseUrl:"",apiMode:"responses",remember:false};',
    'const defaultApiSettings:ApiSettings={provider:"openai",key:"",model:"",baseUrl:"",apiMode:"responses",remember:false,verified:false};',
    "default verified"
)

s = rep(
    s,
    'function makeAsset(file:File, raw:string):AssetFile { return {id:`${Date.now()}-${Math.random()}`,name:file.name,url:URL.createObjectURL(file),raw}; }',
    '''function svgDataUrl(raw:string){ return `data:image/svg+xml;charset=utf-8,${encodeURIComponent(raw)}`; }
function makeAsset(file:File, raw:string):AssetFile { return {id:`${Date.now()}-${Math.random()}`,name:file.name,url:svgDataUrl(raw),raw}; }
function assetToCache(a:AssetFile|null){ return a?{id:a.id,name:a.name,raw:a.raw}:null; }
function assetFromCache(a:any):AssetFile|null { return a?.raw?{id:a.id||`restored-${Date.now()}`,name:a.name||"asset.svg",raw:a.raw,url:svgDataUrl(a.raw)}:null; }
function assetsFromCache(list:any){ return Array.isArray(list)?list.map(assetFromCache).filter(Boolean) as AssetFile[]:[]; }
const WORKSPACE_CACHE_KEY="diw_workspace_v2";
const WORKSPACE_CACHE_VERSION=2;''',
    "persistent asset helper"
)

s = rep(
    s,
    '  const [layouts,setLayouts]=useState<Record<string,DesignLayout>>({});\n  const [currentModel,setCurrentModel]=useState("");',
    '''  const [layouts,setLayouts]=useState<Record<string,DesignLayout>>({});
  const [currentModel,setCurrentModel]=useState("");
  const [deconstructing,setDeconstructing]=useState(false);
  const [workspaceHydrated,setWorkspaceHydrated]=useState(false);
  const skipNextGraphicColorRef=useRef(false);''',
    "workspace persistence state"
)

old_effects = '''  const activeProject=projects.find(p=>p.id===activeProjectId)||projects[0];
  useEffect(()=>{ const api=readApiSettings(); setCurrentModel(api.model||""); },[started,step,section]);
  useEffect(()=>{ if(!graphic) return; const colors=extractSvgColors(graphic.raw); if(colors.length){ setBrandColor(colors[0]); setAuxiliaryColors(colors.slice(1,5)); } },[graphic]);
  useEffect(()=>{ setProjects(prev=>prev.map(p=>p.id===activeProjectId?{...p,step,updatedAt:Date.now()}:p)); },[step,activeProjectId]);'''

new_effects = '''  const activeProject=projects.find(p=>p.id===activeProjectId)||projects[0];

  // 恢复上一次本机工作痕迹。版本号用于未来“大改版”时主动失效旧缓存。
  useEffect(()=>{
    try{
      const raw=localStorage.getItem(WORKSPACE_CACHE_KEY);
      if(raw){
        const d=JSON.parse(raw);
        if(d?.version===WORKSPACE_CACHE_VERSION){
          if(d.section)setSection(d.section);
          if(typeof d.started==="boolean")setStarted(d.started);
          if(d.step)setStep(d.step);
          if(typeof d.dark==="boolean")setDark(d.dark);
          if(Array.isArray(d.projects)&&d.projects.length)setProjects(d.projects);
          if(d.activeProjectId)setActiveProjectId(d.activeProjectId);
          skipNextGraphicColorRef.current=true;
          setGraphic(assetFromCache(d.graphic));
          setCnTexts(assetsFromCache(d.cnTexts));
          setEnTexts(assetsFromCache(d.enTexts));
          if(d.brandColor)setBrandColor(d.brandColor);
          if(Array.isArray(d.auxiliaryColors))setAuxiliaryColors(d.auxiliaryColors);
          if(typeof d.assetsConfirmed==="boolean")setAssetsConfirmed(d.assetsConfirmed);
          if(Array.isArray(d.selectedExtensions))setSelectedExtensions(d.selectedExtensions);
          if(Array.isArray(d.selectedBoundaries))setSelectedBoundaries(d.selectedBoundaries);
          if(d.ratios)setRatios(d.ratios);
          if(Array.isArray(d.materials))setMaterials(d.materials);
          if(typeof d.rulesConfirmed==="boolean")setRulesConfirmed(d.rulesConfirmed);
          if(typeof d.selectedRouteId==="string")setSelectedRouteId(d.selectedRouteId);
          if(d.routeStudies)setRouteStudies(d.routeStudies);
          if(typeof d.selectedStudyId==="string")setSelectedStudyId(d.selectedStudyId);
          if(typeof d.studyConfirmed==="boolean")setStudyConfirmed(d.studyConfirmed);
          if(typeof d.generated==="boolean")setGenerated(d.generated);
          if(Array.isArray(d.approved))setApproved(d.approved);
          if(Array.isArray(d.deleted))setDeleted(d.deleted);
          if(d.layouts)setLayouts(d.layouts);
        }
      }
    }catch(e){ console.warn("workspace restore failed",e); }
    setWorkspaceHydrated(true);
  },[]);

  useEffect(()=>{ const api=readApiSettings(); setCurrentModel(api.model||""); },[started,step,section]);

  useEffect(()=>{
    if(!graphic)return;
    if(skipNextGraphicColorRef.current){skipNextGraphicColorRef.current=false;return;}
    const colors=extractSvgColors(graphic.raw);
    if(colors.length){setBrandColor(colors[0]);setAuxiliaryColors(colors.slice(1,5));}
  },[graphic]);

  useEffect(()=>{ setProjects(prev=>prev.map(p=>p.id===activeProjectId?{...p,step,updatedAt:Date.now()}:p)); },[step,activeProjectId]);

  // 自动保存测试现场：上传 SVG、当前步骤、颜色、解构选择、物料和生成结果。
  useEffect(()=>{
    if(!workspaceHydrated)return;
    const timer=window.setTimeout(()=>{
      try{
        localStorage.setItem(WORKSPACE_CACHE_KEY,JSON.stringify({
          version:WORKSPACE_CACHE_VERSION,
          section,started,step,dark,projects,activeProjectId,
          graphic:assetToCache(graphic),
          cnTexts:cnTexts.map(assetToCache),
          enTexts:enTexts.map(assetToCache),
          brandColor,auxiliaryColors,assetsConfirmed,
          selectedExtensions,selectedBoundaries,ratios,materials,rulesConfirmed,
          selectedRouteId,routeStudies,selectedStudyId,studyConfirmed,
          generated,approved,deleted,layouts
        }));
      }catch(e){ console.warn("workspace autosave failed",e); }
    },250);
    return()=>window.clearTimeout(timer);
  },[
    workspaceHydrated,section,started,step,dark,projects,activeProjectId,
    graphic,cnTexts,enTexts,brandColor,auxiliaryColors,assetsConfirmed,
    selectedExtensions,selectedBoundaries,ratios,materials,rulesConfirmed,
    selectedRouteId,routeStudies,selectedStudyId,studyConfirmed,
    generated,approved,deleted,layouts
  ]);

  const aiBusy=generating||deconstructing;'''

s = rep(s, old_effects, new_effects, "workspace effects")

s = rep(
    s,
    'setMaterials(defaultMaterials.map(x=>({...x}))); setRulesConfirmed(false); setSelectedRouteId(""); setRouteStudies({}); setSelectedStudyId(""); setStudyConfirmed(false); setGenerated(false); setGenerating(false); setApproved([]); setDeleted([]); setLayouts({});',
    'setMaterials(defaultMaterials.map(x=>({...x}))); setRulesConfirmed(false); setSelectedRouteId(""); setRouteStudies({}); setSelectedStudyId(""); setStudyConfirmed(false); setGenerated(false); setGenerating(false); setDeconstructing(false); setApproved([]); setDeleted([]); setLayouts({});',
    "reset deconstructing"
)

s = rep(
    s,
    '  const openCurrent=()=>{ setStep(activeProject?.step||"brand"); setStarted(true); };',
    '  const openCurrent=()=>{ setStep(activeProject?.step||"brand"); setSection("projects"); setStarted(true); };',
    "open current section"
)

s = rep(
    s,
    '  if(!started) return <Home section={section} setSection={setSection} dark={dark} setDark={setDark} projects={projects} activeProjectId={activeProjectId} onStart={openCurrent} onCreateProject={createProject} onSelectProject={switchProject}/>;',
    '  if(!started || section!=="projects") return <Home section={section} setSection={setSection} dark={dark} setDark={setDark} projects={projects} activeProjectId={activeProjectId} onStart={openCurrent} onCreateProject={createProject} onSelectProject={switchProject}/>;',
    "non destructive sidebar navigation"
)

s = rep(
    s,
    'return <main className={`shell ${dark?"dark":""}`}><Sidebar section={section} setSection={setSection} dark={dark} setDark={setDark} onExitWorkflow={()=>setStarted(false)}/><section className="workflow">',
    'return <main className={`shell ${dark?"dark":""}`}><Sidebar section={section} setSection={setSection} dark={dark} setDark={setDark} onExitWorkflow={()=>{}} busy={aiBusy}/><section className="workflow">',
    "workflow sidebar preserve"
)

s = rep(
    s,
    '<header className="topbar"><div><button className="crumb" onClick={()=>setStarted(false)}>项目</button>',
    '<header className="topbar"><div><button className="crumb" disabled={aiBusy} onClick={()=>setStarted(false)}>项目</button>',
    "busy crumb"
)

s = rep(
    s,
    '<div className="stepper">{steps.map((x,i)=><button key={x.id} className={i<=stepIndex?"active":""} onClick={()=>i<=stepIndex&&setStep(x.id)}><i>{i+1}</i>{x.label}</button>)}</div>',
    '<div className="stepper">{steps.map((x,i)=><button key={x.id} className={i<=stepIndex?"active":""} disabled={aiBusy} onClick={()=>!aiBusy&&i<=stepIndex&&setStep(x.id)}><i>{i+1}</i>{x.label}</button>)}</div>',
    "busy stepper"
)

s = rep(
    s,
    'studyConfirmed={studyConfirmed} setStudyConfirmed={setStudyConfirmed} selectedExtensions={selectedExtensions}',
    'studyConfirmed={studyConfirmed} setStudyConfirmed={setStudyConfirmed} setDeconstructing={setDeconstructing} selectedExtensions={selectedExtensions}',
    "deconstruct busy prop"
)

s = rep(
    s,
    '<button className="secondary footer-nav-button" onClick={()=>stepIndex===0?setStarted(false):move(-1)}>← 返回</button>',
    '<button className="secondary footer-nav-button" disabled={aiBusy} onClick={()=>stepIndex===0?setStarted(false):move(-1)}>← 返回</button>',
    "busy back"
)

s = rep(
    s,
    '<button className={`primary footer-nav-button footer-primary ${canContinue?"is-ready":""}`} disabled={!canContinue} onClick={()=>stepIndex<4&&move(1)}>',
    '<button className={`primary footer-nav-button footer-primary ${canContinue&&!aiBusy?"is-ready":""}`} disabled={!canContinue||aiBusy} onClick={()=>stepIndex<4&&move(1)}>',
    "busy continue"
)

old_sidebar = '''function Sidebar({section,setSection,dark,setDark,onExitWorkflow}:{section:Section;setSection:(x:Section)=>void;dark:boolean;setDark:(x:boolean)=>void;onExitWorkflow:()=>void}){ const names:Record<Section,string>={projects:"项目",library:"资料库",settings:"设置"}; const navigate=(target:Section)=>{setSection(target);onExitWorkflow();}; return <aside className="sidebar"><button type="button" className="mark mark-btn" onClick={()=>navigate("projects")}>DI</button><nav>{(["projects","library","settings"] as const).map(x=><button type="button" key={x} className={section===x?"nav-on":""} onClick={()=>navigate(x)}>{names[x]}</button>)}</nav><button type="button" className="theme-toggle" onClick={()=>setDark(!dark)}><span>{dark?"☀":"☾"}</span>{dark?"日间":"黑夜"}</button></aside>; }'''

new_sidebar = '''function Sidebar({section,setSection,dark,setDark,onExitWorkflow,busy=false}:{section:Section;setSection:(x:Section)=>void;dark:boolean;setDark:(x:boolean)=>void;onExitWorkflow:()=>void;busy?:boolean}){ const names:Record<Section,string>={projects:"项目",library:"资料库",settings:"设置"}; const navigate=(target:Section)=>{if(busy&&target!==section)return;setSection(target);onExitWorkflow();}; return <aside className={`sidebar ${busy?"is-busy":""}`}><button type="button" className="mark mark-btn" disabled={busy&&section!=="projects"} onClick={()=>navigate("projects")}>DI</button><nav>{(["projects","library","settings"] as const).map(x=><button type="button" key={x} disabled={busy&&x!==section} className={section===x?"nav-on":""} onClick={()=>navigate(x)}>{names[x]}</button>)}</nav><button type="button" className="theme-toggle" onClick={()=>setDark(!dark)}><span>{dark?"☀":"☾"}</span>{dark?"日间":"黑夜"}</button>{busy&&<small className="sidebar-busy-note">AI 执行中</small>}</aside>; }'''

s = rep(s, old_sidebar, new_sidebar, "busy Sidebar")

s = rep(
    s,
    'function DeconstructionRoutes({graphic,selectedRouteId,setSelectedRouteId,routeStudies,setRouteStudies,selectedStudyId,setSelectedStudyId,studyConfirmed,setStudyConfirmed,selectedExtensions,setSelectedExtensions}:{graphic:AssetFile|null;selectedRouteId:string;setSelectedRouteId:(x:string)=>void;routeStudies:Record<string,DeconstructionStudy[]>;setRouteStudies:(x:Record<string,DeconstructionStudy[]>)=>void;selectedStudyId:string;setSelectedStudyId:(x:string)=>void;studyConfirmed:boolean;setStudyConfirmed:(x:boolean)=>void;selectedExtensions:string[];setSelectedExtensions:(x:string[])=>void}){',
    'function DeconstructionRoutes({graphic,selectedRouteId,setSelectedRouteId,routeStudies,setRouteStudies,selectedStudyId,setSelectedStudyId,studyConfirmed,setStudyConfirmed,setDeconstructing,selectedExtensions,setSelectedExtensions}:{graphic:AssetFile|null;selectedRouteId:string;setSelectedRouteId:(x:string)=>void;routeStudies:Record<string,DeconstructionStudy[]>;setRouteStudies:(x:Record<string,DeconstructionStudy[]>)=>void;selectedStudyId:string;setSelectedStudyId:(x:string)=>void;studyConfirmed:boolean;setStudyConfirmed:(x:boolean)=>void;setDeconstructing:(x:boolean)=>void;selectedExtensions:string[];setSelectedExtensions:(x:string[])=>void}){',
    "DeconstructionRoutes busy signature"
)

s = rep(
    s,
    '    setLoading(true);\n    setError("");',
    '    setLoading(true);\n    setDeconstructing(true);\n    setError("");',
    "deconstruct busy start"
)

s = rep(
    s,
    '    }finally{\n      setLoading(false);\n    }\n  };',
    '    }finally{\n      setLoading(false);\n      setDeconstructing(false);\n    }\n  };',
    "deconstruct busy end"
)

s = rep(
    s,
    'useEffect(()=>{const v=readApiSettings();setProvider(v.provider);setKey(v.key);setModel(v.model);setBaseUrl(v.baseUrl);setApiMode(v.apiMode);setRemember(v.remember);setVerified(false)},[]);',
    'useEffect(()=>{const v=readApiSettings();setProvider(v.provider);setKey(v.key);setModel(v.model);setBaseUrl(v.baseUrl);setApiMode(v.apiMode);setRemember(v.remember);setVerified(!!v.verified)},[]);',
    "restore verified"
)

s = rep(
    s,
    'const current=():ApiSettings=>({provider,key:key.trim(),model:model.trim(),baseUrl:baseUrl.trim(),apiMode,remember});',
    'const current=(verifiedValue=verified):ApiSettings=>({provider,key:key.trim(),model:model.trim(),baseUrl:baseUrl.trim(),apiMode,remember,verified:verifiedValue});',
    "current verified"
)

s = rep(
    s,
    'const save=()=>{if(!key.trim()||!model.trim())return;writeApiSettings(current());setVerified(false);setMessage("配置已保存，建议先测试连接")};',
    'const save=()=>{if(!key.trim()||!model.trim())return;writeApiSettings(current(verified));setMessage(verified?"已保存 · 当前连接验证仍然有效":"配置已保存，建议先测试连接")};',
    "save verified"
)

s = rep(
    s,
    'writeApiSettings(current());setVerified(true);setMessage(`连接成功 · ${model.trim()} · ${apiMode==="responses"?"Responses":"Chat Completions"}`);',
    'writeApiSettings(current(true));setVerified(true);setMessage(`连接成功 · ${model.trim()} · ${apiMode==="responses"?"Responses":"Chat Completions"}`);',
    "test verified persist"
)

tsx.write_text(s, encoding="utf-8")

c = css.read_text(encoding="utf-8")
addon = '''

/* v7.2 — persistent workspace + uninterrupted workflow */
.sidebar.is-busy nav button:disabled,.sidebar.is-busy .mark-btn:disabled{opacity:.32;cursor:not-allowed}
.sidebar-busy-note{position:absolute;left:14px;bottom:58px;font-size:9px;color:#27c768;opacity:.85}
.stepper button:disabled,.crumb:disabled,.footer-nav-button:disabled{cursor:not-allowed}
'''
if "v7.2 — persistent workspace" not in c:
    c += addon
css.write_text(c, encoding="utf-8")

print("完成：")
print("✓ AI 连接验证状态持久化")
print("✓ 侧栏切走再回来恢复原项目步骤")
print("✓ AI 执行时锁住会打断请求的导航")
print("✓ SVG、步骤、色板、解构、物料、布局和结果自动保存在本机")
print("✓ 同域名重新部署/刷新后恢复测试现场")
print("下一步运行：npm run build")
