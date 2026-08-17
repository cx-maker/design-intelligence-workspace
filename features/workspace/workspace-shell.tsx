"use client";

import { ChangeEvent, useMemo, useRef, useState } from "react";

type WorkflowStep = "brand" | "references" | "generate" | "review" | "deliver";
type Section = "projects" | "library" | "settings";
type AssetFile = { name: string; url: string; raw: string } | null;
type Material = { id: string; name: string; description: string; referenceName?: string; referenceUrl?: string };

const steps: { id: WorkflowStep; label: string }[] = [
  { id: "brand", label: "导入资产" },
  { id: "references", label: "确认资产" },
  { id: "generate", label: "延展规则" },
  { id: "review", label: "生成与调整" },
  { id: "deliver", label: "矢量导出" },
];

const defaultMaterials: Material[] = [
  { id: "card", name: "名片", description: "" },
  { id: "bag", name: "手提袋", description: "" },
  { id: "box", name: "包装盒", description: "" },
];

const extensionOptions = ["等比放大", "超大裁切", "局部裁切", "完整展示", "少量重复", "图形拆解", "局部元素提取", "负形利用", "黑白反白", "允许旋转", "连续构图"];
const boundaryOptions = ["不重新设计 Logo", "不改变路径形状", "不增加无关装饰图形", "不使用光效 / 粒子 / 纹理", "不使用阴影", "不使用 3D / 透视", "不使用摄影 Mockup", "保持纯二维正视图"];

export function WorkspaceShell() {
  const [section, setSection] = useState<Section>("projects");
  const [started, setStarted] = useState(false);
  const [step, setStep] = useState<WorkflowStep>("brand");
  const [dark, setDark] = useState(true);
  const [graphic, setGraphic] = useState<AssetFile>(null);
  const [cnText, setCnText] = useState<AssetFile>(null);
  const [enText, setEnText] = useState<AssetFile>(null);
  const [brandColor, setBrandColor] = useState("#008FDB");
  const [assetsConfirmed, setAssetsConfirmed] = useState(false);
  const [selectedExtensions, setSelectedExtensions] = useState<string[]>(["超大裁切", "局部裁切", "完整展示", "黑白反白", "图形拆解"]);
  const [selectedBoundaries, setSelectedBoundaries] = useState<string[]>(boundaryOptions);
  const [materials, setMaterials] = useState<Material[]>(defaultMaterials);
  const [rulesConfirmed, setRulesConfirmed] = useState(false);
  const [generated, setGenerated] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [approved, setApproved] = useState<string[]>([]);

  const stepIndex = steps.findIndex((item) => item.id === step);
  const move = (direction: 1 | -1) => setStep(steps[Math.max(0, Math.min(4, stepIndex + direction))].id);
  const canContinue = useMemo(() => {
    if (step === "brand") return !!graphic;
    if (step === "references") return assetsConfirmed;
    if (step === "generate") return rulesConfirmed && materials.length > 0;
    if (step === "review") return generated;
    return true;
  }, [step, graphic, assetsConfirmed, rulesConfirmed, materials.length, generated]);

  if (!started) {
    return <Home section={section} setSection={setSection} dark={dark} setDark={setDark} onStart={() => setStarted(true)} />;
  }

  return <main className={`shell ${dark ? "dark" : ""}`}>
    <Sidebar section={section} setSection={setSection} dark={dark} setDark={setDark} onHome={() => setStarted(false)} />
    <section className="workflow">
      <header className="topbar"><div><button className="crumb" onClick={() => setStarted(false)}>项目</button><span> / 当前品牌方向</span></div><div className="step-count">第 {stepIndex + 1} 步，共 5 步</div></header>
      <div className="progress"><span style={{ width: `${((stepIndex + 1) / 5) * 100}%` }} /></div>
      <div className="stepper">{steps.map((item, i) => <button key={item.id} className={i <= stepIndex ? "active" : ""} onClick={() => i <= stepIndex && setStep(item.id)}><i>{i + 1}</i>{item.label}</button>)}</div>
      <div className="content">
        {step === "brand" && <ImportAssets graphic={graphic} setGraphic={setGraphic} cnText={cnText} setCnText={setCnText} enText={enText} setEnText={setEnText} />}
        {step === "references" && <ConfirmAssets graphic={graphic} cnText={cnText} enText={enText} brandColor={brandColor} setBrandColor={setBrandColor} confirmed={assetsConfirmed} setConfirmed={setAssetsConfirmed} />}
        {step === "generate" && <Rules selectedExtensions={selectedExtensions} setSelectedExtensions={setSelectedExtensions} selectedBoundaries={selectedBoundaries} setSelectedBoundaries={setSelectedBoundaries} materials={materials} setMaterials={setMaterials} confirmed={rulesConfirmed} setConfirmed={setRulesConfirmed} />}
        {step === "review" && <GenerateAndReview graphic={graphic} brandColor={brandColor} materials={materials} selectedExtensions={selectedExtensions} approved={approved} setApproved={setApproved} generating={generating} setGenerating={setGenerating} generated={generated} setGenerated={setGenerated} />}
        {step === "deliver" && <ExportVectors graphic={graphic} brandColor={brandColor} materials={materials} approved={approved} />}
      </div>
      <footer className="footer"><button className="text-btn" disabled={stepIndex === 0} onClick={() => move(-1)}>← 返回</button><button className="primary footer-primary" disabled={!canContinue} onClick={() => stepIndex < 4 && move(1)}>{stepIndex === 4 ? "已到导出步骤" : "继续 →"}</button></footer>
    </section>
  </main>;
}

function Sidebar({ section, setSection, dark, setDark, onHome }: { section: Section; setSection: (x: Section) => void; dark: boolean; setDark: (x: boolean) => void; onHome: () => void }) {
  const names: Record<Section, string> = { projects: "项目", library: "资料库", settings: "设置" };
  return <aside className="sidebar"><button className="mark mark-btn" onClick={onHome}>DI</button><nav>{(["projects", "library", "settings"] as const).map((item) => <button key={item} className={section === item ? "nav-on" : ""} onClick={() => { setSection(item); onHome(); }}>{names[item]}</button>)}</nav><button className="theme-toggle" onClick={() => setDark(!dark)}><span>{dark ? "☀" : "☾"}</span>{dark ? "日间" : "黑夜"}</button></aside>;
}

function Home({ section, setSection, dark, setDark, onStart }: { section: Section; setSection: (x: Section) => void; dark: boolean; setDark: (x: boolean) => void; onStart: () => void }) {
  return <main className={`shell ${dark ? "dark" : ""}`}><Sidebar section={section} setSection={setSection} dark={dark} setDark={setDark} onHome={() => setSection("projects")} /><section className="home">
    {section === "projects" && <><p className="eyebrow">Design Intelligence Workspace</p><h1>用一个确定的 Logo，快速试出一整套品牌氛围。</h1><p className="muted home-intro">上传图形与文字资产，选择延展方式和物料，让工作台快速生成提案级二维品牌应用。</p><button className="continue-card" onClick={onStart}><div><span>当前项目</span><h2>新品牌方向</h2><p>等待导入 Logo 图形</p></div><b>开始 →</b></button><div className="heading-row"><h3>最近项目</h3><button className="text-btn" onClick={onStart}>+ 新建项目</button></div><div className="empty-projects">最近项目会在保存后出现在这里。</div></>}
    {section === "library" && <Library />}
    {section === "settings" && <Settings />}
  </section></main>;
}

function FileAssetCard({ title, hint, asset, required, onChange }: { title: string; hint: string; asset: AssetFile; required?: boolean; onChange: (x: AssetFile) => void }) {
  const ref = useRef<HTMLInputElement>(null);
  const choose = () => ref.current?.click();
  const load = async (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    if (!file.name.toLowerCase().endsWith(".svg")) { alert("当前版本先仅支持 SVG 矢量文件。"); e.target.value = ""; return; }
    const raw = await file.text();
    const url = URL.createObjectURL(file);
    onChange({ name: file.name, url, raw });
  };
  return <div className={`asset-upload ${asset ? "loaded" : ""}`}><input ref={ref} hidden type="file" accept=".svg,image/svg+xml" onChange={load}/><div className="asset-upload-preview">{asset ? <img src={asset.url} alt="" /> : <span>SVG</span>}</div><div><div className="asset-title-row"><b>{title}</b>{required && <em>必填</em>}</div><p>{asset ? asset.name : hint}</p></div><button className="secondary" onClick={choose}>{asset ? "重新选择" : "选择文件"}</button></div>;
}

function ImportAssets({ graphic, setGraphic, cnText, setCnText, enText, setEnText }: { graphic: AssetFile; setGraphic: (x: AssetFile) => void; cnText: AssetFile; setCnText: (x: AssetFile) => void; enText: AssetFile; setEnText: (x: AssetFile) => void }) {
  return <div className="single wide-single"><p className="eyebrow">第 1 步 · 导入资产</p><h1>先把 Logo 图形和文字分开交给工作台。</h1><p className="muted">当前版本只接收 SVG。图形必填，中英文文字资产可选；不让 AI 猜拆分关系，减少识别误差。</p><div className="asset-upload-stack"><FileAssetCard title="Logo 图形" hint="上传已经定稿的图形主体 SVG" required asset={graphic} onChange={setGraphic}/><FileAssetCard title="中文文字资产" hint="可选：上传中文标准字 / 中文组合 SVG" asset={cnText} onChange={setCnText}/><FileAssetCard title="英文文字资产" hint="可选：上传英文标准字 / 英文组合 SVG" asset={enText} onChange={setEnText}/></div><div className="notice"><b>为什么分开上传？</b><p>图文组合本身也是版式。先保留最确定的图形与文字资产，后续再让 AI 决定如何组合，比自动拆 Logo 更可靠。</p></div></div>;
}

function ConfirmAssets({ graphic, cnText, enText, brandColor, setBrandColor, confirmed, setConfirmed }: { graphic: AssetFile; cnText: AssetFile; enText: AssetFile; brandColor: string; setBrandColor: (x: string) => void; confirmed: boolean; setConfirmed: (x: boolean) => void }) {
  return <div className="single wide-single"><p className="eyebrow">第 2 步 · 确认资产</p><h1>确认后面允许使用的品牌原料。</h1><p className="muted">这里不再做自动拆解，只确认你主动提交的资产和基础配色。</p><div className="asset-confirm-grid"><AssetPreview title="Logo 图形" asset={graphic}/><AssetPreview title="中文" asset={cnText}/><AssetPreview title="英文" asset={enText}/></div><div className="color-row"><div><span>品牌主色</span><b>{brandColor.toUpperCase()}</b></div><input type="color" value={brandColor} onChange={(e) => setBrandColor(e.target.value)} /><input className="hex-input" value={brandColor.toUpperCase()} onChange={(e) => /^#[0-9A-Fa-f]{0,6}$/.test(e.target.value) && setBrandColor(e.target.value)} /></div><label className="confirm-check"><input type="checkbox" checked={confirmed} onChange={(e) => setConfirmed(e.target.checked)} /><span>确认：后续生成只使用已提交的 Logo 图形、文字资产与品牌配色，不重新设计 Logo。</span></label></div>;
}

function AssetPreview({ title, asset }: { title: string; asset: AssetFile }) { return <div className="asset-preview-card"><span>{title}</span><div>{asset ? <img src={asset.url} alt="" /> : <small>未提供</small>}</div><b>{asset?.name || "—"}</b></div>; }

function ToggleChips({ options, selected, setSelected }: { options: string[]; selected: string[]; setSelected: (x: string[]) => void }) {
  const toggle = (x: string) => setSelected(selected.includes(x) ? selected.filter(y => y !== x) : [...selected, x]);
  return <div className="choice-grid">{options.map(x => <button key={x} className={selected.includes(x) ? "selected" : ""} onClick={() => toggle(x)}>{selected.includes(x) ? "✓ " : "+ "}{x}</button>)}</div>;
}

function Rules({ selectedExtensions, setSelectedExtensions, selectedBoundaries, setSelectedBoundaries, materials, setMaterials, confirmed, setConfirmed }: { selectedExtensions: string[]; setSelectedExtensions: (x: string[]) => void; selectedBoundaries: string[]; setSelectedBoundaries: (x: string[]) => void; materials: Material[]; setMaterials: (x: Material[]) => void; confirmed: boolean; setConfirmed: (x: boolean) => void }) {
  const updateMaterial = (id: string, patch: Partial<Material>) => setMaterials(materials.map(m => m.id === id ? { ...m, ...patch } : m));
  const addMaterial = () => setMaterials([...materials, { id: `custom-${Date.now()}`, name: "新物料", description: "" }]);
  const removeMaterial = (id: string) => setMaterials(materials.filter(m => m.id !== id));
  const refInput = async (id: string, e: ChangeEvent<HTMLInputElement>) => { const f=e.target.files?.[0]; if(!f) return; updateMaterial(id,{referenceName:f.name,referenceUrl:URL.createObjectURL(f)}); };
  return <div className="rules-page"><p className="eyebrow">第 3 步 · 延展规则</p><h1>把你的判断变成 AI 的设计指令。</h1><p className="muted">每一个选择都会进入后续生成指令。没有绝对正确答案，你可以针对不同 Logo 方向快速试不同组合。</p><section className="rule-card full"><span className="rule-tag">Logo 延展方式 · 多选</span><ToggleChips options={extensionOptions} selected={selectedExtensions} setSelected={setSelectedExtensions}/></section><section className="rule-card full"><span className="rule-tag">配色规则</span><h3>黑 / 白 / 品牌主色优先</h3><div className="palette"><i className="p-black"/><i className="p-white"/><i className="p-blue"/></div><p>大主视觉保持品牌标准色；小 Logo 在深色背景识别不足时允许白色单色版。</p></section><section className="rule-card full"><span className="rule-tag">视觉边界 · 多选</span><ToggleChips options={boundaryOptions} selected={selectedBoundaries} setSelected={setSelectedBoundaries}/></section><section className="rule-card full"><div className="rule-head"><div><span className="rule-tag">首轮物料</span><h3>告诉 AI 这次要做什么。</h3></div><button className="secondary" onClick={addMaterial}>+ 新增物料</button></div><div className="material-editor-list">{materials.map((m, index) => <div className="material-editor" key={m.id}><div className="material-number">{String(index+1).padStart(2,"0")}</div><div className="material-fields"><input value={m.name} onChange={(e)=>updateMaterial(m.id,{name:e.target.value})}/><textarea value={m.description} onChange={(e)=>updateMaterial(m.id,{description:e.target.value})} placeholder="设计描述（选填）。例如：黑底、Logo 超大裁切，整体克制、留白多……"/><label className="reference-upload"><input type="file" accept="image/*" hidden onChange={(e)=>refInput(m.id,e)}/>{m.referenceName ? `参考图：${m.referenceName}` : "+ 上传参考图（选填）"}</label></div><button className="remove-btn" onClick={()=>removeMaterial(m.id)}>删除</button></div>)}</div></section><label className="confirm-check"><input type="checkbox" checked={confirmed} onChange={(e)=>setConfirmed(e.target.checked)} /><span>使用以上选择作为本轮 AI 生成指令。</span></label></div>;
}

function GenerateAndReview({ graphic, brandColor, materials, selectedExtensions, approved, setApproved, generating, setGenerating, generated, setGenerated }: { graphic: AssetFile; brandColor: string; materials: Material[]; selectedExtensions: string[]; approved: string[]; setApproved: (x: string[]) => void; generating: boolean; setGenerating: (x: boolean) => void; generated: boolean; setGenerated: (x: boolean) => void }) {
  const generate = () => { setGenerating(true); setTimeout(()=>{setGenerating(false);setGenerated(true)},1200); };
  const toggle = (id:string)=>setApproved(approved.includes(id)?approved.filter(x=>x!==id):[...approved,id]);
  return <div className="review-page"><p className="eyebrow">第 4 步 · 生成与调整</p><h1>{generated ? "第一轮结果出来了，直接在这里判断。" : "生成第一轮品牌应用。"}</h1><p className="muted">当前先用前端模板模拟；下一轮接 API 后，这里会由 AI 根据第 3 步指令生成结构化版式方案。</p>{!generated && <button className="primary large generate-btn" onClick={generate} disabled={generating}>{generating ? "生成中…" : "生成第一轮"}</button>}{generated && <div className="result-list">{materials.map((m,i)=><article className="result-card" key={m.id}><div className={`result-art result-${i%3}`} style={{"--brand" : brandColor} as React.CSSProperties}>{graphic && <img src={graphic.url} alt=""/>}<small>{m.name}</small></div><div className="result-meta"><b>{m.name}</b><span>{m.description || `AI 自由发挥 · ${selectedExtensions.slice(0,3).join(" / ")}`}</span><div><button className={approved.includes(m.id)?"approved":""} onClick={()=>toggle(m.id)}>{approved.includes(m.id)?"已保留 ✓":"保留"}</button><button>调整</button><button onClick={()=>setGenerated(false)}>重做</button></div></div></article>)}</div>}</div>;
}

function ExportVectors({ graphic, brandColor, materials, approved }: { graphic: AssetFile; brandColor: string; materials: Material[]; approved: string[] }) {
  const targets = approved.length ? materials.filter(m=>approved.includes(m.id)) : materials;
  const downloadSvg = (m:Material,index:number)=>{
    const inner = graphic?.raw?.replace(/<\?xml[^>]*>/g,"") || "";
    const safeInner = inner.replace(/<svg([^>]*)>/i, '<g>').replace(/<\/svg>/i,'</g>');
    const bg = index%3===0 ? "#111111" : index%3===1 ? "#ffffff" : brandColor;
    const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="800" viewBox="0 0 1200 800"><rect width="1200" height="800" fill="${bg}"/><g transform="translate(620 120) scale(2.2)">${safeInner}</g><text x="64" y="740" font-family="Arial" font-size="26" fill="${bg==='#ffffff'?'#111111':'#ffffff'}">${m.name}</text></svg>`;
    const blob=new Blob([svg],{type:"image/svg+xml"}); const url=URL.createObjectURL(blob); const a=document.createElement("a");a.href=url;a.download=`${m.name}.svg`;a.click();URL.revokeObjectURL(url);
  };
  return <div className="single wide-single"><p className="eyebrow">第 5 步 · 矢量导出</p><h1>只处理最终文件。</h1><p className="muted">保留的物料会在这里导出为 SVG。当前导出器已经使用你上传的原始 SVG 资产，不重新绘制 Logo。</p><div className="export-list">{targets.map((m,i)=><div key={m.id}><div><b>{m.name}</b><span>SVG · 原始 Logo 路径保留</span></div><button className="secondary" onClick={()=>downloadSvg(m,i)}>导出 SVG</button></div>)}</div><p className="export-note">下一阶段可增加：整套 ZIP、PDF 提案预览、Illustrator 兼容导出。</p></div>;
}

function Library(){ return <><p className="eyebrow">资料库</p><h1>参考与历史资产。</h1><p className="muted">这里后续用于保存你上传过的 Logo、文字资产、参考图和成功的延展规则。</p><div className="empty-projects">当前还没有保存的资料。</div></>; }
function Settings(){ return <><p className="eyebrow">设置</p><h1>工作台设置。</h1><p className="muted">下一阶段将在这里配置 OpenAI API Key、本地存储和默认输出规则。</p><div className="settings-placeholder"><b>OpenAI API</b><span>尚未配置</span><button className="secondary">稍后接入</button></div></>; }
