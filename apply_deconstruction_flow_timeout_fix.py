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

s = rep(
    s,
    '  const [selectedStudyId,setSelectedStudyId]=useState<string>("");\n  const [generated,setGenerated]=useState(false);',
    '  const [selectedStudyId,setSelectedStudyId]=useState<string>("");\n  const [studyConfirmed,setStudyConfirmed]=useState(false);\n  const [generated,setGenerated]=useState(false);',
    "studyConfirmed state"
)

s = rep(
    s,
    'setMaterials(defaultMaterials.map(x=>({...x}))); setRulesConfirmed(false); setSelectedRouteId(""); setRouteStudies({}); setSelectedStudyId(""); setGenerated(false);',
    'setMaterials(defaultMaterials.map(x=>({...x}))); setRulesConfirmed(false); setSelectedRouteId(""); setRouteStudies({}); setSelectedStudyId(""); setStudyConfirmed(false); setGenerated(false);',
    "reset studyConfirmed"
)

s = rep(
    s,
    'step==="generate"?!!selectedRouteId:',
    'step==="generate"?(!!selectedStudyId&&studyConfirmed):',
    "generate step canContinue"
)

s = rep(
    s,
    '[step,graphic,assetsConfirmed,selectedRouteId,generated,approved.length]',
    '[step,graphic,assetsConfirmed,selectedStudyId,studyConfirmed,generated,approved.length]',
    "canContinue dependencies"
)

s = rep(
    s,
    'routeStudies={routeStudies} setRouteStudies={setRouteStudies} selectedStudyId={selectedStudyId} setSelectedStudyId={setSelectedStudyId} selectedExtensions={selectedExtensions}',
    'routeStudies={routeStudies} setRouteStudies={setRouteStudies} selectedStudyId={selectedStudyId} setSelectedStudyId={setSelectedStudyId} studyConfirmed={studyConfirmed} setStudyConfirmed={setStudyConfirmed} selectedExtensions={selectedExtensions}',
    "DeconstructionRoutes confirmation props"
)

start = s.index('function DeconstructionRoutes(')
end = s.index('\n\nfunction Rules(', start)

new_func = '''function DeconstructionRoutes({graphic,selectedRouteId,setSelectedRouteId,routeStudies,setRouteStudies,selectedStudyId,setSelectedStudyId,studyConfirmed,setStudyConfirmed,selectedExtensions,setSelectedExtensions}:{graphic:AssetFile|null;selectedRouteId:string;setSelectedRouteId:(x:string)=>void;routeStudies:Record<string,DeconstructionStudy[]>;setRouteStudies:(x:Record<string,DeconstructionStudy[]>)=>void;selectedStudyId:string;setSelectedStudyId:(x:string)=>void;studyConfirmed:boolean;setStudyConfirmed:(x:boolean)=>void;selectedExtensions:string[];setSelectedExtensions:(x:string[])=>void}){
  const toggle=(x:string)=>{
    setSelectedExtensions(selectedExtensions.includes(x)?selectedExtensions.filter(v=>v!==x):[...selectedExtensions,x]);
    setStudyConfirmed(false);
  };
  const [loading,setLoading]=useState(false);
  const [error,setError]=useState("");

  const chooseRoute=(routeId:string)=>{
    if(routeId!==selectedRouteId){
      setSelectedRouteId(routeId);
      setSelectedStudyId("");
      setRouteStudies({});
      setStudyConfirmed(false);
    }
  };

  const chooseStudy=(routeId:string,studyId:string)=>{
    setSelectedRouteId(routeId);
    setSelectedStudyId(studyId);
    setStudyConfirmed(false);
  };

  const generateStudies=async()=>{
    if(!selectedRouteId){setError("先选择一个解构方向。");return;}
    const api=readApiSettings();
    if(!api.key||!api.model){setError("请先到「设置」完成 AI 连接。");return;}
    setLoading(true);
    setError("");
    setSelectedStudyId("");
    setStudyConfirmed(false);
    try{
      const logoImage=await svgUrlToPngDataUrl(graphic?.url);
      const route=routePresets.find(x=>x.id===selectedRouteId);
      const r=await fetch("/api/design",{method:"POST",headers:{"Content-Type":"application/json","x-openai-key":api.key},body:JSON.stringify({
        mode:"deconstruct",model:api.model,provider:api.provider,baseUrl:api.baseUrl,apiMode:api.apiMode,
        logoImage,routes:route?[route]:[],selectedExtensions
      })});
      const d=await r.json();
      if(!r.ok)throw new Error(d.error||"解构失败");
      const studies=(d.studies||[]) as DeconstructionStudy[];
      setRouteStudies({[selectedRouteId]:studies});
    }catch(e){
      setError(e instanceof Error?e.message:"解构失败");
    }finally{
      setLoading(false);
    }
  };

  const studies=selectedRouteId?(routeStudies[selectedRouteId]||[]):[];

  return <div className="deconstruction-page">
    <p className="eyebrow">第 3 步 · 理解并解构 Logo</p>
    <h1>先决定这个 Logo 最值得往哪里发展。</h1>
    <p className="muted">先选发展方向和约束，再让 AI 生成纯图形解构。确认其中一个小样后，才进入平面物料。</p>

    <div className="deconstruction-intro">
      <div className="deconstruction-logo white-preview">{graphic?<img src={graphic.url} alt="Logo"/>:<span>Logo</span>}</div>
      <div>
        <span className="rule-tag">当前分析原则</span>
        <p>优先寻找：可重复单元、比例、负形、裁切、局部识别点、空间和尺度关系。</p>
        <p>暂不处理：文字、Mockup、材质、光影、摄影氛围。</p>
      </div>
    </div>

    <section className="deconstruction-stage">
      <div className="stage-label"><i>1</i><div><b>先选一个发展方向</b><span>这里只决定设计思路，不立即调用 AI。</span></div></div>
      <div className="route-grid compact-routes">
        {routePresets.map((r,i)=><button type="button" key={r.id} className={`route-card route-choice-card ${selectedRouteId===r.id?"selected":""}`} onClick={()=>chooseRoute(r.id)}>
          <div className="route-index">0{i+1}</div>
          <h3>{r.title}</h3>
          <p>{r.summary}</p>
          <div className="route-tags">{r.tags.map(t=><span key={t}>{t}</span>)}</div>
          <b>{selectedRouteId===r.id?"已选择 ✓":"选择这个方向"}</b>
        </button>)}
      </div>
    </section>

    <section className="deconstruction-stage">
      <div className="stage-label"><i>2</i><div><b>再补充约束</b><span>这些条件会和选中的方向一起发送给 AI。</span></div></div>
      <div className="route-guidance">
        <div className="choice-grid">
          {extensionOptions.map(x=><button type="button" key={x} className={selectedExtensions.includes(x)?"selected":""} onClick={()=>toggle(x)}>{selectedExtensions.includes(x)?"✓ ":"+ "}{x}</button>)}
        </div>
      </div>
    </section>

    <section className="deconstruction-stage generate-stage">
      <div className="stage-label"><i>3</i><div><b>生成纯图形解构</b><span>只使用原 Logo 的复制、裁切、尺度、旋转、留白和空间关系。</span></div></div>
      {error&&<div className="api-error">{error}</div>}
      <button className="primary large deconstruct-bottom-btn" onClick={generateStudies} disabled={loading||!graphic||!selectedRouteId}>
        {loading?"AI 正在生成解构…":studies.length?"重新生成这条路线":"开始生成图形解构"}
      </button>

      {loading&&<div className="deconstruct-loading"><span/><p>正在分析 Logo 结构并尝试视觉关系，这一步通常比普通文字请求更慢。</p></div>}

      {studies.length>0&&<div className="study-results">
        <div className="study-results-head"><b>选择一个小样作为下一步的视觉规则</b><span>选择后还需要确认。</span></div>
        <div className="study-results-grid">
          {studies.map(st=><button key={st.id} type="button" className={`route-study large-study ${selectedStudyId===st.id?"selected":""}`} onClick={()=>chooseStudy(selectedRouteId,st.id)}>
            <StudyVisual study={st} graphic={graphic}/>
            <span>{st.title}</span>
            <small>{st.note}</small>
          </button>)}
        </div>
        <button className={`confirm-study-btn ${selectedStudyId?"ready":""} ${studyConfirmed?"confirmed":""}`} disabled={!selectedStudyId} onClick={()=>setStudyConfirmed(true)}>
          {studyConfirmed?"已确认，可进入下一步 ✓":"确认这个解构方向"}
        </button>
      </div>}
    </section>
  </div>;
}'''

s = s[:start] + new_func + s[end:]
tsx.write_text(s, encoding="utf-8")

r = api.read_text(encoding="utf-8")
r = rep(r,'async function relayFetch(url:string, init:RequestInit){','async function relayFetch(url:string, init:RequestInit, timeoutMs=30000){',"relay timeout arg")
r = rep(r,'      signal: AbortSignal.timeout(30000),','      signal: AbortSignal.timeout(timeoutMs),',"relay timeout usage")

decon_start = r.index('  if(mode==="deconstruct"){')
decon_end = r.index('\n\n  const prompt=mode==="adjust"', decon_start)
block = r[decon_start:decon_end]
block = block.replace('temperature:0.65})});const data:any=', 'temperature:0.65})},120000);const data:any=', 1)
block = block.replace('name:"logo_deconstruction",strict:true,schema}}})});const data:any=', 'name:"logo_deconstruction",strict:true,schema}}})},120000);const data:any=', 1)
block = block.replace('minItems:routes.length*2,maxItems:routes.length*2','minItems:routes.length*4,maxItems:routes.length*4',1)
block = block.replace('每条路线生成 2 个不同实验','当前只处理用户选中的一条路线，并生成 4 个明显不同的实验',1)
r = r[:decon_start] + block + r[decon_end:]
api.write_text(r, encoding="utf-8")

c = css.read_text(encoding="utf-8")
addon = '''

/* v7.1 — staged deconstruction flow */
.deconstruction-stage{margin-top:18px;padding:14px;border:1px solid var(--line);border-radius:12px;background:rgba(255,255,255,.015)}
.stage-label{display:flex;align-items:center;gap:10px;margin-bottom:12px}
.stage-label>i{width:23px;height:23px;border-radius:50%;display:grid;place-items:center;background:#fff;color:#111;font-size:10px;font-style:normal;font-weight:800}
.stage-label>div{display:grid;gap:2px}.stage-label b{font-size:11px}.stage-label span{font-size:9px;opacity:.5}
.compact-routes .route-choice-card{padding:14px!important;cursor:pointer;min-height:174px}
.route-choice-card>b{display:block;margin-top:12px;color:#27c768;font-size:9px}
.generate-stage{padding-bottom:18px}.deconstruct-bottom-btn{width:100%;min-height:46px;margin-top:4px}
.deconstruct-loading{display:flex;align-items:center;justify-content:center;gap:10px;padding:20px 0 4px}
.deconstruct-loading span{width:16px;height:16px;border:2px solid rgba(255,255,255,.18);border-top-color:#27c768;border-radius:50%;animation:spin .8s linear infinite}
.deconstruct-loading p{font-size:9px;opacity:.55;margin:0}
@keyframes spin{to{transform:rotate(360deg)}}
.study-results{margin-top:16px}.study-results-head{display:flex;justify-content:space-between;align-items:center;margin-bottom:9px}.study-results-head b{font-size:10px}.study-results-head span{font-size:9px;opacity:.5}
.study-results-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:9px}.large-study .study-visual{height:150px}
.confirm-study-btn{display:block;margin:14px 0 0 auto;border:1px solid var(--line);border-radius:7px;background:transparent;color:var(--muted);padding:9px 14px;font-weight:700}
.confirm-study-btn.ready{background:#fff;color:#111;border-color:#fff}.confirm-study-btn.confirmed{background:#27c768;color:#fff;border-color:#27c768}
@media(max-width:1000px){.study-results-grid{grid-template-columns:1fr 1fr}}
'''
if "v7.1 — staged deconstruction flow" not in c:
    c += addon
css.write_text(c, encoding="utf-8")

print("完成：")
print("✓ 解构 API 超时由 30 秒提高到 120 秒（仅解构请求）")
print("✓ 第三步改为：选方向 → 选约束 → 底部生成 → 选小样 → 明确确认")
print("✓ 继续按钮只有“选中小样 + 已确认”后才可用")
print("✓ 单次只生成当前选中路线，降低请求负担，并生成 4 个解构小样")
print("下一步运行：npm run build")
