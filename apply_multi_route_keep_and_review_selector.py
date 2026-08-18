from pathlib import Path

p = Path.cwd() / "features/workspace/workspace-shell.tsx"
s = p.read_text(encoding="utf-8")

def rep(old, new, label, count=1):
    global s
    if old not in s:
        raise SystemExit(f"[失败] 找不到替换点：{label}")
    s = s.replace(old, new, count)

rep(
    '  const [selectedStudyId,setSelectedStudyId]=useState<string>("");\n  const [studyConfirmed,setStudyConfirmed]=useState(false);',
    '  const [selectedStudyId,setSelectedStudyId]=useState<string>("");\n  const [keptStudyIds,setKeptStudyIds]=useState<string[]>([]);\n  const [studyConfirmed,setStudyConfirmed]=useState(false);',
    'keptStudyIds state'
)

rep(
    '          if(typeof d.selectedStudyId==="string")setSelectedStudyId(d.selectedStudyId);\n          if(typeof d.studyConfirmed==="boolean")setStudyConfirmed(d.studyConfirmed);',
    '          if(typeof d.selectedStudyId==="string")setSelectedStudyId(d.selectedStudyId);\n          if(Array.isArray(d.keptStudyIds))setKeptStudyIds(d.keptStudyIds);\n          if(typeof d.studyConfirmed==="boolean")setStudyConfirmed(d.studyConfirmed);',
    'restore kept studies'
)

rep(
    '          selectedRouteId,routeStudies,selectedStudyId,studyConfirmed,\n          generated,approved,deleted,layouts',
    '          selectedRouteId,routeStudies,selectedStudyId,keptStudyIds,studyConfirmed,\n          generated,approved,deleted,layouts',
    'save kept studies'
)

rep(
    '    selectedRouteId,routeStudies,selectedStudyId,studyConfirmed,\n    generated,approved,deleted,layouts',
    '    selectedRouteId,routeStudies,selectedStudyId,keptStudyIds,studyConfirmed,\n    generated,approved,deleted,layouts',
    'autosave dependency kept studies'
)

rep(
    'setSelectedRouteId(""); setRouteStudies({}); setSelectedStudyId(""); setStudyConfirmed(false);',
    'setSelectedRouteId(""); setRouteStudies({}); setSelectedStudyId(""); setKeptStudyIds([]); setStudyConfirmed(false);',
    'reset kept studies'
)

rep(
    'step==="generate"?(!!selectedStudyId&&studyConfirmed)',
    'step==="generate"?(keptStudyIds.length>0&&studyConfirmed)',
    'continue condition'
)

rep(
    '[step,graphic,assetsConfirmed,selectedStudyId,studyConfirmed,generated,approved.length]',
    '[step,graphic,assetsConfirmed,keptStudyIds.length,studyConfirmed,generated,approved.length]',
    'continue dependency'
)

rep(
    'selectedStudyId={selectedStudyId} setSelectedStudyId={setSelectedStudyId} studyConfirmed={studyConfirmed}',
    'selectedStudyId={selectedStudyId} setSelectedStudyId={setSelectedStudyId} keptStudyIds={keptStudyIds} setKeptStudyIds={setKeptStudyIds} studyConfirmed={studyConfirmed}',
    'deconstruction props'
)

rep(
    'selectedRoute={routePresets.find(x=>x.id===selectedRouteId)||null} selectedStudy={Object.values(routeStudies).flat().find(x=>x.id===selectedStudyId)||null}/>',
    'selectedRoute={routePresets.find(x=>x.id===selectedRouteId)||null} selectedStudy={Object.values(routeStudies).flat().find(x=>x.id===selectedStudyId)||null} keptStudies={Object.values(routeStudies).flat().filter(x=>keptStudyIds.includes(x.id))}/>',
    'review kept studies prop'
)

rep(
    'function DeconstructionRoutes({graphic,selectedRouteId,setSelectedRouteId,routeStudies,setRouteStudies,selectedStudyId,setSelectedStudyId,studyConfirmed,setStudyConfirmed,setDeconstructing,selectedExtensions,setSelectedExtensions}:{graphic:AssetFile|null;selectedRouteId:string;setSelectedRouteId:(x:string)=>void;routeStudies:Record<string,DeconstructionStudy[]>;setRouteStudies:(x:Record<string,DeconstructionStudy[]>)=>void;selectedStudyId:string;setSelectedStudyId:(x:string)=>void;studyConfirmed:boolean;setStudyConfirmed:(x:boolean)=>void;setDeconstructing:(x:boolean)=>void;selectedExtensions:string[];setSelectedExtensions:(x:string[])=>void}){',
    'function DeconstructionRoutes({graphic,selectedRouteId,setSelectedRouteId,routeStudies,setRouteStudies,selectedStudyId,setSelectedStudyId,keptStudyIds,setKeptStudyIds,studyConfirmed,setStudyConfirmed,setDeconstructing,selectedExtensions,setSelectedExtensions}:{graphic:AssetFile|null;selectedRouteId:string;setSelectedRouteId:(x:string)=>void;routeStudies:Record<string,DeconstructionStudy[]>;setRouteStudies:React.Dispatch<React.SetStateAction<Record<string,DeconstructionStudy[]>>>;selectedStudyId:string;setSelectedStudyId:(x:string)=>void;keptStudyIds:string[];setKeptStudyIds:React.Dispatch<React.SetStateAction<string[]>>;studyConfirmed:boolean;setStudyConfirmed:(x:boolean)=>void;setDeconstructing:(x:boolean)=>void;selectedExtensions:string[];setSelectedExtensions:(x:string[])=>void}){',
    'DeconstructionRoutes signature'
)

rep(
    '      setSelectedRouteId(routeId);\n      setSelectedStudyId("");\n      setRouteStudies({});\n      setStudyConfirmed(false);',
    '      setSelectedRouteId(routeId);\n      setSelectedStudyId("");\n      setStudyConfirmed(false);',
    'route switching persistence'
)

s = s.replace(
    'setRouteStudies({[selectedRouteId]:[...allStudies]});',
    'setRouteStudies(prev=>({...prev,[selectedRouteId]:[...allStudies]}));'
)

s = s.replace('<div className="stage-label"><i>1</i><div><b>先选一个发展方向</b>', '<div className="stage-label"><i>A</i><div><b>先选一个发展方向</b>')
s = s.replace('<div className="stage-label"><i>2</i><div><b>再补充约束</b>', '<div className="stage-label"><i>B</i><div><b>再补充约束</b>')
s = s.replace('<div className="stage-label"><i>3</i><div><b>生成纯图形解构</b>', '<div className="stage-label"><i>C</i><div><b>生成纯图形解构</b>')

rep(
    'className={`route-study large-study ${selectedStudyId===st.id?"selected":""}`}',
    'className={`route-study large-study ${selectedStudyId===st.id?"selected":""} ${keptStudyIds.includes(st.id)?"kept":""}`}',
    'study kept class'
)

old_confirm = '''        <button className={`confirm-study-btn ${selectedStudyId?"ready":""} ${studyConfirmed?"confirmed":""}`} disabled={!selectedStudyId} onClick={()=>setStudyConfirmed(true)}>
          {studyConfirmed?"已确认，可进入下一步 ✓":"确认这个解构方向"}
        </button>'''

new_confirm = '''        <div className="keep-study-actions">
          <button
            className={`confirm-study-btn ${selectedStudyId?"ready":""} ${selectedStudyId&&keptStudyIds.includes(selectedStudyId)?"confirmed":""}`}
            disabled={!selectedStudyId}
            onClick={()=>{
              if(!selectedStudyId)return;
              setKeptStudyIds(prev=>prev.includes(selectedStudyId)?prev.filter(id=>id!==selectedStudyId):[...prev,selectedStudyId]);
              setStudyConfirmed(false);
            }}
          >
            {selectedStudyId&&keptStudyIds.includes(selectedStudyId)?"取消保留":"保留这个小样"}
          </button>
          {keptStudyIds.length>0&&<button
            className={`confirm-study-btn ready ${studyConfirmed?"confirmed":""}`}
            onClick={()=>setStudyConfirmed(true)}
          >
            {studyConfirmed?`已确认 ${keptStudyIds.length} 个方向，可进入下一步 ✓`:`确认保留的 ${keptStudyIds.length} 个方向`}
          </button>}
        </div>'''
rep(old_confirm, new_confirm, 'keep and confirm buttons')

rep(
    'function GenerateAndReview({graphic,brandColor,auxiliaryColors,ratios,selectedBoundaries,materials,setMaterials,layouts,setLayouts,selectedExtensions,approved,setApproved,deleted,setDeleted,generating,setGenerating,generated,setGenerated,currentModel,selectedRoute,selectedStudy}:{graphic:AssetFile|null;brandColor:string;auxiliaryColors:string[];ratios:Ratios;selectedBoundaries:string[];materials:Material[];setMaterials:(x:Material[])=>void;layouts:Record<string,DesignLayout>;setLayouts:React.Dispatch<React.SetStateAction<Record<string,DesignLayout>>>;selectedExtensions:string[];approved:string[];setApproved:(x:string[])=>void;deleted:string[];setDeleted:(x:string[])=>void;generating:boolean;setGenerating:(x:boolean)=>void;generated:boolean;setGenerated:(x:boolean)=>void;currentModel:string;selectedRoute:DeconstructionRoute|null;selectedStudy:DeconstructionStudy|null}){',
    'function GenerateAndReview({graphic,brandColor,auxiliaryColors,ratios,selectedBoundaries,materials,setMaterials,layouts,setLayouts,selectedExtensions,approved,setApproved,deleted,setDeleted,generating,setGenerating,generated,setGenerated,currentModel,selectedRoute,selectedStudy,keptStudies=[]}:{graphic:AssetFile|null;brandColor:string;auxiliaryColors:string[];ratios:Ratios;selectedBoundaries:string[];materials:Material[];setMaterials:(x:Material[])=>void;layouts:Record<string,DesignLayout>;setLayouts:React.Dispatch<React.SetStateAction<Record<string,DesignLayout>>>;selectedExtensions:string[];approved:string[];setApproved:(x:string[])=>void;deleted:string[];setDeleted:(x:string[])=>void;generating:boolean;setGenerating:(x:boolean)=>void;generated:boolean;setGenerated:(x:boolean)=>void;currentModel:string;selectedRoute:DeconstructionRoute|null;selectedStudy:DeconstructionStudy|null;keptStudies?:DeconstructionStudy[]}){',
    'GenerateAndReview signature'
)

rep(
    '  const [error,setError]=useState("");',
    '  const [error,setError]=useState("");\n  const [activeStudyId,setActiveStudyId]=useState<string>(()=>keptStudies[0]?.id||selectedStudy?.id||"");\n  const activeStudy=keptStudies.find(x=>x.id===activeStudyId)||selectedStudy||keptStudies[0]||null;',
    'active review study state'
)

rep(
    'deconstructionRoute:selectedRoute,deconstructionStudy:selectedStudy',
    'deconstructionRoute:routePresets.find(r=>r.id===activeStudy?.routeId)||selectedRoute,deconstructionStudy:activeStudy',
    'generation context active study'
)

old_heading = '''    <div className="review-heading-row">
      <div>
        <h1>{generated?"先判断平面系统是否成立。":"选几个物料，验证这条视觉路线。"}</h1>
        <p className="muted">这一层只看二维正视图、比例、留白、图形关系和信息层级。效果图留到下一步。</p>
      </div>
      <div className="review-badges"><div className="model-badge"><span>当前模型</span><b>{currentModel||"未配置"}</b></div><div className="model-badge"><span>当前路线</span><b>{selectedRoute?.title||"未选择"}</b></div></div>
    </div>'''

new_heading = '''    <div className="review-heading-row">
      <div>
        <h1>{generated?"先判断平面系统是否成立。":"选几个物料，验证这条视觉路线。"}</h1>
        <p className="muted">这一层只看二维正视图、比例、留白、图形关系和信息层级。效果图留到下一步。</p>
      </div>
      <div className="review-badges"><div className="model-badge"><span>当前模型</span><b>{currentModel||"未配置"}</b></div><div className="model-badge"><span>当前路线</span><b>{(routePresets.find(r=>r.id===activeStudy?.routeId)||selectedRoute)?.title||"未选择"}</b></div></div>
    </div>
    {keptStudies.length>1&&<section className="kept-route-selector">
      <div><b>本轮保留了 {keptStudies.length} 个方向</b><span>先选一个做平面初排；其他方向仍然保留，可以随时切换再试。</span></div>
      <div className="kept-route-grid">
        {keptStudies.map(st=><button key={st.id} type="button" className={activeStudy?.id===st.id?"selected":""} onClick={()=>setActiveStudyId(st.id)}>
          <StudyVisual study={st} graphic={graphic}/>
          <span>{routePresets.find(r=>r.id===st.routeId)?.title||"解构方向"}</span>
          <small>{st.title}</small>
        </button>)}
      </div>
    </section>}'''
rep(old_heading, new_heading, 'review route selector')

p.write_text(s, encoding="utf-8")

css = Path.cwd() / "features/workspace/workspace-shell.css"
c = css.read_text(encoding="utf-8")
addon = r'''

/* v7.3 — multi-route keep flow */
.route-study.kept{box-shadow:inset 0 0 0 1px #27c768}
.keep-study-actions{display:flex;justify-content:flex-end;gap:8px;margin-top:14px}
.kept-route-selector{margin:14px 0 18px;padding:12px;border:1px solid var(--line);border-radius:10px}
.kept-route-selector>div:first-child{display:flex;justify-content:space-between;align-items:center;margin-bottom:10px}
.kept-route-selector>div:first-child b{font-size:10px}
.kept-route-selector>div:first-child span{font-size:9px;opacity:.55}
.kept-route-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:8px}
.kept-route-grid button{border:1px solid var(--line);background:transparent;border-radius:8px;padding:6px;text-align:left;color:inherit}
.kept-route-grid button.selected{border-color:#27c768;box-shadow:inset 0 0 0 1px #27c768}
.kept-route-grid .study-visual{height:88px;border-radius:5px;overflow:hidden}
.kept-route-grid button>span,.kept-route-grid button>small{display:block;margin-top:6px}
.kept-route-grid button>span{font-size:9px;font-weight:700}
.kept-route-grid button>small{font-size:8px;opacity:.55}
'''
if "v7.3 — multi-route keep flow" not in c:
    c += addon
css.write_text(c, encoding="utf-8")

print("完成：")
print("✓ 不同路线的已生成解构结果互不覆盖")
print("✓ 小样支持保留 / 取消保留，可跨路线保留多个")
print("✓ 至少保留 1 个并最终确认后，继续按钮才可用")
print("✓ 第四步会显示所有保留方向，可再次选择哪个方向做平面初排")
print("✓ 平面生成会使用第四步当前选择的解构小样")
print("✓ 第三步三个子步骤序号改为 A / B / C")
print("✓ 保留状态继续写入现有本地缓存")
print("下一步运行：npm run build")
