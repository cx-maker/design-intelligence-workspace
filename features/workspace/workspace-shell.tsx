"use client";

import { useMemo, useState } from "react";
import Image from "next/image";
import { candidates, references as initialReferences } from "@/mock/data";
import { buildMockContext } from "@/services/context-builder.service";
import { AestheticReference, QuickScore, WorkflowStep } from "@/schemas/domain";

const steps: { id: WorkflowStep; label: string }[] = [
  { id: "brand", label: "品牌" }, { id: "references", label: "参考" }, { id: "generate", label: "生成" }, { id: "review", label: "选择" }, { id: "deliver", label: "交付" },
];
const labels: Record<QuickScore, string> = { strong: "♥", like: "👍", neutral: "—", reject: "×" };

export function WorkspaceShell() {
  const [section, setSection] = useState<"projects" | "library" | "settings">("projects");
  const [started, setStarted] = useState(false);
  const [step, setStep] = useState<WorkflowStep>("brand");
  const [refs, setRefs] = useState(initialReferences);
  const [activeRef, setActiveRef] = useState("r1");
  const [detail, setDetail] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [selectedCandidate, setSelectedCandidate] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);
  const [dark, setDark] = useState(false);
  const stepIndex = steps.findIndex((item) => item.id === step);
  const currentRef = refs.find((item) => item.id === activeRef) ?? refs[0];
  const selectedRefs = refs.filter((item) => item.score && item.score !== "reject");
  const context = useMemo(() => buildMockContext(selectedRefs), [selectedRefs]);
  const move = (direction: 1 | -1) => setStep(steps[Math.max(0, Math.min(4, stepIndex + direction))].id);
  const score = (value: QuickScore) => setRefs((items) => items.map((item) => item.id === activeRef ? { ...item, score: value } : item));

  if (!started) return <Home onStart={() => setStarted(true)} section={section} setSection={setSection} dark={dark} setDark={setDark} />;

  return <main className={`shell ${dark ? "dark" : ""}`}><Sidebar section={section} setSection={setSection} dark={dark} setDark={setDark} /><section className="workflow">
    <header className="topbar"><div><button className="crumb" onClick={() => setStarted(false)}>项目</button><span> / 唐睛眼视光</span></div><div className="step-count">第 {stepIndex + 1} 步，共 5 步</div></header>
    <div className="progress"><span style={{ width: `${((stepIndex + 1) / 5) * 100}%` }} /></div>
    <div className="stepper">{steps.map((item, i) => <div key={item.id} className={i <= stepIndex ? "active" : ""}><i>{i + 1}</i>{item.label}</div>)}</div>
    <div className="content">
      {step === "brand" && <Brand onNext={() => move(1)} />}
      {step === "references" && <References refs={refs} current={currentRef} onSelect={setActiveRef} onScore={score} detail={detail} setDetail={setDetail} />}
      {step === "generate" && <Generate generating={generating} setGenerating={setGenerating} context={context} />}
      {step === "review" && <Review selected={selectedCandidate} onSelect={setSelectedCandidate} />}
      {step === "deliver" && <Deliver selected={selectedCandidate} saved={saved} setSaved={setSaved} />}
    </div>
    <footer className="footer"><button className="text-btn" disabled={stepIndex === 0} onClick={() => move(-1)}>← 返回</button><button className="primary" onClick={() => stepIndex === 4 ? setSaved(true) : move(1)}>{stepIndex === 4 ? "导出模拟包" : "继续 →"}</button></footer>
  </section></main>;
}

function Sidebar({ section, setSection, dark, setDark }: { section: string; setSection: (x: "projects" | "library" | "settings") => void; dark: boolean; setDark: (x: boolean) => void }) { const names = { projects: "项目", library: "资料库", settings: "设置" }; return <aside className="sidebar"><div className="mark">DI</div><nav>{(["projects", "library", "settings"] as const).map((item) => <button key={item} className={section === item ? "nav-on" : ""} onClick={() => setSection(item)}>{names[item]}</button>)}</nav><button className="theme-toggle" onClick={() => setDark(!dark)} aria-label="切换日间或黑夜主题"><span>{dark ? "☀" : "☾"}</span>{dark ? "日间" : "黑夜"}</button></aside>; }
function Home({ onStart, section, setSection, dark, setDark }: { onStart: () => void; section: string; setSection: (x: "projects" | "library" | "settings") => void; dark: boolean; setDark: (x: boolean) => void }) { return <main className={`shell ${dark ? "dark" : ""}`}><Sidebar section={section} setSection={setSection} dark={dark} setDark={setDark}/><section className="home"><p className="eyebrow">设计智能工作台</p>{section === "projects" ? <><h1>从上次停下的地方继续。</h1><button className="continue-card" onClick={onStart}><div><span>继续项目</span><h2>唐睛眼视光</h2><p>视觉方向 · 第 2 步，共 5 步</p></div><b>继续 →</b></button><div className="heading-row"><h3>最近项目</h3><button className="text-btn" onClick={onStart}>+ 新建项目</button></div><div className="project-grid">{["丝奢", "咖啡品牌"].map((name, i) => <button className="project-card" key={name} onClick={onStart}><span className={`swatch s${i}`}/><h3>{name}</h3><p>{i ? "参考" : "选择"} · 继续 →</p></button>)}</div></> : section === "library" ? <Library /> : <Settings />}</section></main>; }
function Brand({ onNext }: { onNext: () => void }) { return <div className="single"><p className="eyebrow">第 1 步 · 品牌</p><h1>先认识一下这个品牌。</h1><p className="muted">我们会为你准备合适的工作流。</p><div className="brand-card"><div className="logo-box">T</div><div><b>唐睛眼视光</b><p>Logo 已分析 ✓</p><span className="color-dot"/> 检测到的品牌色 <b>#008FDB</b></div></div><div className="recommend"><span>推荐工作流</span><b>品牌视觉识别</b><p>推荐资料库：通用品牌 · 医疗 / 视光</p></div><button className="primary large" onClick={onNext}>确认无误</button><button className="text-btn centered">修改</button></div>; }
function References({ refs, current, onSelect, onScore, detail, setDetail }: { refs: AestheticReference[]; current: AestheticReference; onSelect: (id: string) => void; onScore: (x: QuickScore) => void; detail: boolean; setDetail: (x: boolean) => void }) { const scoreText: Record<QuickScore, string> = { strong: "非常喜欢", like: "喜欢", neutral: "一般", reject: "不喜欢" }; return <div><div className="reference-heading"><div><p className="eyebrow">第 2 步 · 参考</p><h1>哪一种感觉更对？</h1><p className="muted">相信第一反应，细节可以稍后补充。</p></div><span className="counter">已评分 {refs.filter(r => r.score).length} 张</span></div><div className="reference-layout"><div className="reference-grid">{refs.map((ref) => <button className={`reference ${ref.id === current.id ? "selected" : ""}`} key={ref.id} onClick={() => onSelect(ref.id)}><Image src={ref.image} alt="" width={900} height={700}/><div><b>{ref.title}</b><span>{ref.score ? labels[ref.score] : "评分"}</span></div></button>)}</div><div className="rating-panel"><Image src={current.image} alt="当前参考图" width={900} height={500}/><p className="eyebrow">你的感受</p><h2>{current.title}</h2><div className="rating-options">{(["strong", "like", "neutral", "reject"] as QuickScore[]).map((value) => <button onClick={() => onScore(value)} className={current.score === value ? "rated" : ""} key={value}><i>{labels[value]}</i>{scoreText[value]}</button>)}</div><label>为什么？ <span>选填</span><textarea placeholder="几个词就够了…" /></label><button className="detail-trigger" onClick={() => setDetail(!detail)}>细化评分 {detail ? "−" : "+"}</button>{detail && <div className="detailed">{["构图", "字体", "色彩", "品牌识别", "商业成熟度", "克制感", "原创性", "系统思维", "动态潜力"].map(x => <label key={x}>{x}<input type="range" min="1" max="10" step=".5" defaultValue="7" /></label>)}</div>}</div></div></div>; }
function Generate({ generating, setGenerating, context }: { generating: boolean; setGenerating: (x: boolean) => void; context: object }) { return <div className="single generate"><p className="eyebrow">第 3 步 · 生成</p><h1>{generating ? "正在构建视觉方向…" : "已准备好生成。"}</h1><div className="check-list"><p>品牌 <b>✓</b></p><p>参考图 <b>✓</b></p><p>偏好 <b>✓</b></p></div>{generating ? <div className="run-status"><span className="spinner"/>正在分析品牌…<br/>正在检索参考…<br/>正在构建方向…<br/>正在生成…</div> : <><button className="primary large" onClick={() => { setGenerating(true); setTimeout(() => setGenerating(false), 2300); }}>生成视觉方向</button><details><summary>高级 · 查看上下文</summary><pre>{JSON.stringify(context, null, 2)}</pre></details></>}</div>; }
function Review({ selected, onSelect }: { selected: string | null; onSelect: (x: string) => void }) { return <div><p className="eyebrow">第 4 步 · 选择</p><h1>哪个方向最接近你的想法？</h1><p className="muted">你的选择会帮助工作台理解你的审美。</p><div className="candidate-grid">{candidates.map((c) => <button onClick={() => onSelect(c.id)} className={`candidate ${selected === c.id ? "choice" : ""}`} key={c.id}><div className="candidate-art" style={{ background: c.color }}><span>{c.name}</span><i/></div><h2>方向 {c.name}</h2><p>{c.description}</p>{selected === c.id && <b>已选择 ✓</b>}</button>)}</div>{selected && <div className="reason"><b>为什么选择这个方向？</b><div>{["构图更好", "识别度更高", "更符合品牌", "更有辨识度", "其他"].map(x => <button key={x}>{x}</button>)}</div><button className="text-btn">跳过</button></div>}</div>; }
function Deliver({ selected, saved, setSaved }: { selected: string | null; saved: boolean; setSaved: (x: boolean) => void }) { const pick = candidates.find(c => c.id === selected) ?? candidates[0]; return <div className="single deliver"><p className="eyebrow">第 5 步 · 交付</p><h1>方向 {pick.name} 已准备就绪。</h1><div className="deliver-preview" style={{ background: pick.color }}><span>唐睛<br/>眼视光</span><i/></div><div className="file-row"><span>已选方向</span><b>{pick.name}</b></div><div className="file-row"><span>文件</span><b>预览 · 导出</b></div><button className="primary large" onClick={() => setSaved(true)}>{saved ? "模拟包已保存 ✓" : "导出模拟包"}</button></div>; }
function Library() { return <><h1>你的审美资料库。</h1><p className="muted">私有的本地参考库，会随着每一次选择变得更懂你。</p><div className="library-list">{[["通用品牌", "124"], ["字体", "48"], ["包装", "82"], ["医疗 / 视光", "36"]].map(([name,count]) => <div key={name}><span className="library-icon">◒</span><b>{name}</b><small>{count} 个参考 · 私有 · 本地</small><button>打开 →</button></div>)}</div></>; }
function Settings() { return <><h1>设置</h1><p className="muted">平时保持简单，需要时再深入。</p><div className="settings-list"><div><b>AI</b><span>已连接 ✓</span><button>管理</button></div><div><b>本地资料库</b><span>已连接 ✓</span><button>管理</button></div><div><b>高级</b><span>Agent Runtime · Codex</span><button>打开</button></div></div></>; }
