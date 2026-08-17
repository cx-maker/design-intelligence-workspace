"use client";

import { useMemo, useState } from "react";

type WorkflowStep = "brand" | "references" | "generate" | "review" | "deliver";
type Section = "projects" | "library" | "settings";

const steps: { id: WorkflowStep; label: string }[] = [
  { id: "brand", label: "导入 Logo" },
  { id: "references", label: "确认资产" },
  { id: "generate", label: "延展规则" },
  { id: "review", label: "生成应用" },
  { id: "deliver", label: "审核导出" },
];

const materials = [
  { id: "bag", name: "品牌平面横版手提袋设计", short: "横版手提袋", variant: "黑底 · 超大裁切", scale: "320%" },
  { id: "poster", name: "品牌平面海报", short: "品牌海报", variant: "白底 · 大比例主视觉", scale: "220%" },
  { id: "box", name: "品牌平面包装盒设计", short: "包装盒", variant: "品牌色底 · 完整展示", scale: "100%" },
];

export function WorkspaceShell() {
  const [section, setSection] = useState<Section>("projects");
  const [started, setStarted] = useState(false);
  const [step, setStep] = useState<WorkflowStep>("brand");
  const [dark, setDark] = useState(false);
  const [logoLoaded, setLogoLoaded] = useState(false);
  const [assetsConfirmed, setAssetsConfirmed] = useState(false);
  const [rulesConfirmed, setRulesConfirmed] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [generated, setGenerated] = useState(false);
  const [approved, setApproved] = useState<string[]>([]);
  const [saved, setSaved] = useState(false);

  const stepIndex = steps.findIndex((item) => item.id === step);
  const move = (direction: 1 | -1) => setStep(steps[Math.max(0, Math.min(4, stepIndex + direction))].id);
  const canContinue = useMemo(() => {
    if (step === "brand") return logoLoaded;
    if (step === "references") return assetsConfirmed;
    if (step === "generate") return rulesConfirmed;
    if (step === "review") return generated;
    return true;
  }, [step, logoLoaded, assetsConfirmed, rulesConfirmed, generated]);

  if (!started) {
    return <Home onStart={() => setStarted(true)} section={section} setSection={setSection} dark={dark} setDark={setDark} />;
  }

  return (
    <main className={`shell ${dark ? "dark" : ""}`}>
      <Sidebar section={section} setSection={setSection} dark={dark} setDark={setDark} />
      <section className="workflow">
        <header className="topbar">
          <div><button className="crumb" onClick={() => setStarted(false)}>项目</button><span> / 唐睛眼视光</span></div>
          <div className="step-count">第 {stepIndex + 1} 步，共 5 步</div>
        </header>
        <div className="progress"><span style={{ width: `${((stepIndex + 1) / 5) * 100}%` }} /></div>
        <div className="stepper">
          {steps.map((item, i) => <div key={item.id} className={i <= stepIndex ? "active" : ""}><i>{i + 1}</i>{item.label}</div>)}
        </div>
        <div className="content">
          {step === "brand" && <ImportLogo loaded={logoLoaded} setLoaded={setLogoLoaded} />}
          {step === "references" && <ConfirmAssets confirmed={assetsConfirmed} setConfirmed={setAssetsConfirmed} />}
          {step === "generate" && <Rules confirmed={rulesConfirmed} setConfirmed={setRulesConfirmed} />}
          {step === "review" && <GenerateApplications generating={generating} setGenerating={setGenerating} generated={generated} setGenerated={setGenerated} />}
          {step === "deliver" && <ReviewAndExport approved={approved} setApproved={setApproved} saved={saved} setSaved={setSaved} />}
        </div>
        <footer className="footer">
          <button className="text-btn" disabled={stepIndex === 0} onClick={() => move(-1)}>← 返回</button>
          <button className="primary" disabled={!canContinue} onClick={() => stepIndex === 4 ? setSaved(true) : move(1)}>
            {stepIndex === 4 ? "导出品牌视觉方案" : "继续 →"}
          </button>
        </footer>
      </section>
    </main>
  );
}

function Sidebar({ section, setSection, dark, setDark }: { section: Section; setSection: (x: Section) => void; dark: boolean; setDark: (x: boolean) => void }) {
  const names: Record<Section, string> = { projects: "项目", library: "资料库", settings: "设置" };
  return <aside className="sidebar"><div className="mark">DI</div><nav>{(["projects", "library", "settings"] as const).map((item) => <button key={item} className={section === item ? "nav-on" : ""} onClick={() => setSection(item)}>{names[item]}</button>)}</nav><button className="theme-toggle" onClick={() => setDark(!dark)}><span>{dark ? "☀" : "☾"}</span>{dark ? "日间" : "黑夜"}</button></aside>;
}

function Home({ onStart, section, setSection, dark, setDark }: { onStart: () => void; section: Section; setSection: (x: Section) => void; dark: boolean; setDark: (x: boolean) => void }) {
  return <main className={`shell ${dark ? "dark" : ""}`}><Sidebar section={section} setSection={setSection} dark={dark} setDark={setDark}/><section className="home"><p className="eyebrow">Design Intelligence Workspace</p>{section === "projects" ? <><h1>基于已有 Logo，生成统一的品牌视觉延展。</h1><p className="muted home-intro">不重新设计标志。先识别并确认品牌资产，再用同一套规则生成克制、现代的二维平面应用。</p><button className="continue-card" onClick={onStart}><div><span>继续项目</span><h2>唐睛眼视光</h2><p>Logo 已导入 · 品牌资产待确认</p></div><b>继续 →</b></button><div className="heading-row"><h3>最近项目</h3><button className="text-btn" onClick={onStart}>+ 新建项目</button></div><div className="project-grid"><button className="project-card" onClick={onStart}><span className="swatch s0"/><h3>丝奢</h3><p>延展规则 · 继续 →</p></button><button className="project-card" onClick={onStart}><span className="swatch s1"/><h3>咖啡品牌</h3><p>审核应用 · 继续 →</p></button></div></> : section === "library" ? <Library /> : <Settings />}</section></main>;
}

function ImportLogo({ loaded, setLoaded }: { loaded: boolean; setLoaded: (x: boolean) => void }) {
  return <div className="single wide-single"><p className="eyebrow">第 1 步 · 导入 Logo</p><h1>先把已经定稿的 Logo 交给工作台。</h1><p className="muted">这里只负责识别和拆分，不重新设计、不变形、不优化标志。</p><div className={`upload-card ${loaded ? "loaded" : ""}`}><div className="upload-mark">{loaded ? "T" : "+"}</div><div><b>{loaded ? "唐睛眼视光 · Logo.svg" : "上传矢量 Logo"}</b><p>{loaded ? "SVG · 已读取图形与文字组合" : "推荐 SVG / PDF / AI 导出的 SVG"}</p></div><button className="secondary" onClick={() => setLoaded(true)}>{loaded ? "重新选择" : "选择文件"}</button></div>{loaded && <div className="notice"><b>接下来会识别</b><p>图形主体 · 中文组合 · 英文组合 · 主色 · 辅助色 · 黑白版本</p></div>}</div>;
}

function ConfirmAssets({ confirmed, setConfirmed }: { confirmed: boolean; setConfirmed: (x: boolean) => void }) {
  const rows = [
    ["图形主体", "原始图形 · 保持轮廓 / 比例 / 叠压关系"],
    ["中文组合", "唐睛眼视光"],
    ["英文组合", "TANGJING VISION"],
    ["品牌主色", "#008FDB"],
    ["辅助色", "黑 #111111 · 白 #FFFFFF"],
    ["单色版本", "黑色 / 白色反白"],
  ];
  return <div className="single wide-single"><p className="eyebrow">第 2 步 · 确认品牌资产</p><h1>把后面要用的东西先准备好。</h1><p className="muted">这一步像“备菜”。确认后，生成阶段只能使用这些既有品牌资产。</p><div className="asset-board"><div className="asset-preview"><div className="logo-super">T</div><small>图形主体预览</small></div><div className="asset-list">{rows.map(([name, value]) => <div key={name}><span>{name}</span><b>{value}</b><button>修改</button></div>)}</div></div><label className="confirm-check"><input type="checkbox" checked={confirmed} onChange={(e) => setConfirmed(e.target.checked)} /><span>确认：后续不得重新设计、变形、圆角化、抽象化或替换 Logo 图形。</span></label></div>;
}

function Rules({ confirmed, setConfirmed }: { confirmed: boolean; setConfirmed: (x: boolean) => void }) {
  const allowed = ["等比放大", "局部裁切", "完整展示", "少量重复", "黑白反白"];
  const forbidden = ["重新设计 Logo", "变形 / 圆角化", "额外装饰图形", "速度线 / 数据线 / 网格", "光效 / 粒子 / 纹理 / 阴影", "透视 / 3D / Mockup / 摄影感"];
  return <div className="rules-page"><div><p className="eyebrow">第 3 步 · 延展规则</p><h1>先锁定规则，再开始生成。</h1><p className="muted">默认目标：极简、现代、国际化、二维、矢量、克制、有秩序。</p></div><div className="rules-grid"><section className="rule-card"><span className="rule-tag">Logo 使用</span><h3>只使用原始 Logo 图形</h3><div className="chip-row">{allowed.map(x => <span key={x}>{x}</span>)}</div><p>主视觉局部裁切时建议占画面 180%–500%；完整展示时必须和信息区形成明确对齐。</p></section><section className="rule-card"><span className="rule-tag">配色</span><h3>黑 / 白 / 品牌色优先</h3><div className="palette"><i className="p-black"/><i className="p-white"/><i className="p-blue"/></div><p>大主视觉保持品牌标准色；小 Logo 在黑底识别不足时可使用白色单色版。</p></section><section className="rule-card full"><span className="rule-tag">禁止项</span><h3>保持绝对二维平面</h3><div className="forbidden-grid">{forbidden.map(x => <span key={x}>× {x}</span>)}</div></section><section className="rule-card full"><span className="rule-tag">首轮物料</span><h3>生成 3 类品牌应用</h3><div className="material-list">{materials.map(m => <div key={m.id}><b>{m.short}</b><span>{m.variant}</span><small>主视觉 {m.scale}</small></div>)}</div></section></div><label className="confirm-check"><input type="checkbox" checked={confirmed} onChange={(e) => setConfirmed(e.target.checked)} /><span>使用以上规则作为本项目的默认品牌延展约束。</span></label></div>;
}

function GenerateApplications({ generating, setGenerating, generated, setGenerated }: { generating: boolean; setGenerating: (x: boolean) => void; generated: boolean; setGenerated: (x: boolean) => void }) {
  const start = () => {
    setGenerating(true);
    setTimeout(() => { setGenerating(false); setGenerated(true); }, 1800);
  };
  return <div><p className="eyebrow">第 4 步 · 生成品牌应用</p><h1>{generating ? "正在构建统一的品牌延展…" : generated ? "第一轮品牌应用已生成。" : "准备生成第一轮应用。"}</h1><p className="muted">同一套品牌系统，不是三个不同 Logo 方向。</p>{generating ? <div className="run-status big-status"><span className="spinner"/>读取品牌资产…<br/>锁定 Logo 结构…<br/>应用二维与配色约束…<br/>生成手提袋 / 海报 / 包装盒…</div> : generated ? <div className="application-grid">{materials.map((m, i) => <article className={`application-card v${i}`} key={m.id}><div className="flat-art"><span className="mini-logo">T</span><b>T</b><small>{m.short}<br/>TANGJING VISION</small></div><div><h3>{m.short}</h3><p>{m.variant} · 主视觉 {m.scale}</p></div></article>)}</div> : <div className="generation-ready"><div className="check-list"><p>品牌资产 <b>✓</b></p><p>Logo 使用规则 <b>✓</b></p><p>二维 / 配色 / 版式约束 <b>✓</b></p><p>3 类目标物料 <b>✓</b></p></div><button className="primary large" onClick={start}>生成品牌应用</button></div>}</div>;
}

function ReviewAndExport({ approved, setApproved, saved, setSaved }: { approved: string[]; setApproved: (x: string[]) => void; saved: boolean; setSaved: (x: boolean) => void }) {
  const toggle = (id: string) => setApproved(approved.includes(id) ? approved.filter(x => x !== id) : [...approved, id]);
  return <div><p className="eyebrow">第 5 步 · 审核与导出</p><h1>逐个确认，不满意的单独重做。</h1><p className="muted">保持整体系统不变，只调整某一物料的裁切、底色或排版。</p><div className="review-grid">{materials.map((m, i) => <article className="review-card" key={m.id}><div className={`review-art rv${i}`}><span>T</span><small>{m.short}</small></div><div className="review-actions"><b>{m.short}</b><span>{m.variant}</span><div><button className={approved.includes(m.id) ? "approved" : ""} onClick={() => toggle(m.id)}>{approved.includes(m.id) ? "已保留 ✓" : "保留"}</button><button>调整</button><button>重做</button></div></div></article>)}</div><div className="export-summary"><span>已保留 {approved.length} / {materials.length} 款</span><button className="primary" onClick={() => setSaved(true)}>{saved ? "品牌视觉方案已保存 ✓" : "导出品牌视觉方案"}</button></div></div>;
}

function Library() { return <><h1>品牌资产与规则库。</h1><p className="muted">保存已经确认过的 Logo 资产、颜色与延展规则，供后续项目复用。</p><div className="library-list">{[["Logo 资产", "8"], ["品牌色", "12"], ["延展规则", "5"], ["二维应用模板", "18"]].map(([name,count]) => <div key={name}><span className="library-icon">◒</span><b>{name}</b><small>{count} 项 · 私有 · 本地</small><button>打开 →</button></div>)}</div></>; }
function Settings() { return <><h1>设置</h1><p className="muted">平时保持简单，需要时再深入。</p><div className="settings-list"><div><b>AI 图像服务</b><span>已连接 ✓</span><button>管理</button></div><div><b>本地品牌资产库</b><span>已连接 ✓</span><button>管理</button></div><div><b>高级</b><span>Agent Runtime</span><button>打开</button></div></div></>; }
