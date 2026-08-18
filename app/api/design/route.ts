import { NextRequest, NextResponse } from "next/server";

async function relayFetch(url:string, init:RequestInit, timeoutMs=30000){
  try {
    return await fetch(url, {
      ...init,
      redirect: "follow",
      signal: AbortSignal.timeout(timeoutMs),
    });
  } catch (e:any) {
    const cause=e?.cause;
    const detail=[e?.message,cause?.code,cause?.message].filter(Boolean).join(" / ");
    throw new Error(`无法连接中转 API：${detail || "未知网络错误"}；请求地址：${url}`);
  }
}

async function readResponse(r:Response){
  const raw=await r.text();
  if(!raw)return {};
  try{return JSON.parse(raw)}catch{
    const compact=raw.replace(/<script[\s\S]*?<\/script>/gi," ").replace(/<style[\s\S]*?<\/style>/gi," ").replace(/<[^>]+>/g," ").replace(/\s+/g," ").trim();
    if(r.status===504||/gateway timeout/i.test(compact))return {message:"中转服务网关超时（504）。这不是 API Key 失效；请求在第三方中转层等待模型返回时被截断。已改为更轻的分批生成，请重试。"};
    if(r.status>=500)return {message:`中转服务暂时异常 (${r.status})${compact?` · ${compact.slice(0,160)}`:""}`};
    return {raw:compact.slice(0,500)||raw.slice(0,500)};
  }
}

const layoutItem = {
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
const studyElement = {type:"object",additionalProperties:false,required:["x","y","scale","rotation","opacity","clip"],properties:{x:{type:"number",minimum:-20,maximum:120},y:{type:"number",minimum:-20,maximum:120},scale:{type:"number",minimum:12,maximum:180},rotation:{type:"number",minimum:-90,maximum:90},opacity:{type:"number",minimum:0.15,maximum:1},clip:{type:"string",enum:["none","left","right","top","bottom","center"]}}};
const deconstructionStudyItem = {type:"object",additionalProperties:false,required:["id","routeId","title","note","background","invert","elements"],properties:{id:{type:"string"},routeId:{type:"string"},title:{type:"string"},note:{type:"string"},background:{type:"string"},invert:{type:"boolean"},elements:{type:"array",minItems:1,maxItems:8,items:studyElement}}};

function safeBaseUrl(provider:string,raw?:string){
  if(provider==="openai")return "https://api.openai.com/v1";
  if(!raw)throw new Error("请填写中转 API Base URL");
  let url:URL;try{url=new URL(raw)}catch{throw new Error("Base URL 格式不正确")}
  if(url.protocol!=="https:")throw new Error("中转 API 仅允许 HTTPS 地址");
  const h=url.hostname.toLowerCase();
  const blocked=h==="localhost"||h==="0.0.0.0"||h==="::1"||/^127\./.test(h)||/^10\./.test(h)||/^192\.168\./.test(h)||/^169\.254\./.test(h)||/^172\.(1[6-9]|2\d|3[01])\./.test(h)||h.endsWith(".local")||h==="metadata.google.internal";
  if(blocked)throw new Error("该 Base URL 不允许使用");
  return url.toString().replace(/\/+$/,"");
}
function extractJson(text:string){return JSON.parse(text.trim().replace(/^```(?:json)?\s*/i,"").replace(/\s*```$/,""))}

export async function POST(req:NextRequest){
 try{
  const key=req.headers.get("x-openai-key");if(!key)return NextResponse.json({error:"请先配置 API Key"},{status:401});
  const body=await req.json();
  const {mode,model,provider="openai",baseUrl,apiMode="responses",logoImage,materials=[],references=[],context,currentLayout,instruction,routes=[],selectedExtensions=[],studyCount=4,batchIndex=0}=body;
  if(!model)return NextResponse.json({error:"请填写模型名"},{status:400});
  const base=safeBaseUrl(provider,baseUrl);

  if(mode==="test"){
   const url=apiMode==="chat"?`${base}/chat/completions`:`${base}/responses`;
   const payload=apiMode==="chat"?{model,messages:[{role:"user",content:"Reply only with OK"}],max_tokens:8,temperature:0}:{model,store:false,input:"Reply only with OK",max_output_tokens:16};
   const r=await relayFetch(url,{method:"POST",headers:{"Authorization":`Bearer ${key}`,"Content-Type":"application/json"},body:JSON.stringify(payload)});
   const d:any=await readResponse(r);
   if(!r.ok)return NextResponse.json({error:d?.error?.message||d?.message||d?.raw||`连接失败 (${r.status})`,status:r.status,statusText:r.statusText,requestUrl:url,finalUrl:r.url},{status:r.status});
   return NextResponse.json({ok:true,model,provider,apiMode,status:r.status,requestUrl:url,finalUrl:r.url});
  }
  if(mode==="deconstruct"){
   const count=Math.max(1,Math.min(4,Number(studyCount)||2));const schema={type:"object",additionalProperties:false,required:["studies"],properties:{studies:{type:"array",minItems:count,maxItems:count,items:deconstructionStudyItem}}};
   const prompt=`你是一名资深品牌图形系统设计师。只针对上传 Logo 做纯图形解构，不写文案、不做 Mockup、不增加无关新形状。当前只处理用户选中的一条路线，并生成 ${count} 个明显不同的实验；这是第 ${Number(batchIndex)+1} 批，请尽量避开常规居中、平均分布等已经容易想到的构图；elements 只能是原 Logo 的复制、缩放、旋转、裁切、局部露出、重复和空间关系。geometry 强调比例/阵列，negative 强调留白/缺省，symbol 强调识别局部/重复节奏，spatial 强调超大尺度/边缘裁切。路线：${JSON.stringify(routes)}。允许延展：${JSON.stringify(selectedExtensions)}。background 只用 #FFFFFF、#111111、#E8E8E8。只返回合法 JSON。`;
   if(apiMode==="chat"){const content:any[]=[{type:"text",text:`${prompt}\nJSON Schema：${JSON.stringify(schema)}`}];if(logoImage)content.push({type:"text",text:"原始 Logo："},{type:"image_url",image_url:{url:logoImage}});const url=`${base}/chat/completions`;const ai=await relayFetch(url,{method:"POST",headers:{"Authorization":`Bearer ${key}`,"Content-Type":"application/json"},body:JSON.stringify({model,messages:[{role:"system",content:"只输出合法 JSON，不要 Markdown。"},{role:"user",content}],temperature:0.65})},120000);const data:any=await readResponse(ai);if(!ai.ok)return NextResponse.json({error:data?.error?.message||data?.message||data?.raw||`API 请求失败 (${ai.status})`},{status:ai.status});const text=data?.choices?.[0]?.message?.content;if(!text)return NextResponse.json({error:"模型没有返回解构结果"},{status:502});try{return NextResponse.json(extractJson(text))}catch{return NextResponse.json({error:"模型返回的解构结果不是有效 JSON"},{status:502})}}
   const content:any[]=[{type:"input_text",text:prompt}];if(logoImage)content.push({type:"input_text",text:"下面是原始 Logo："},{type:"input_image",image_url:logoImage,detail:"high"});const url=`${base}/responses`;const ai=await relayFetch(url,{method:"POST",headers:{"Authorization":`Bearer ${key}`,"Content-Type":"application/json"},body:JSON.stringify({model,store:false,input:[{role:"user",content}],text:{format:{type:"json_schema",name:"logo_deconstruction",strict:true,schema}}})},120000);const data:any=await readResponse(ai);if(!ai.ok)return NextResponse.json({error:data?.error?.message||data?.message||data?.raw||`API 请求失败 (${ai.status})`},{status:ai.status});const text=data.output?.flatMap((x:any)=>x.content||[]).find((x:any)=>x.type==="output_text")?.text;if(!text)return NextResponse.json({error:"API 没有返回解构结果"},{status:502});return NextResponse.json(JSON.parse(text));
  }

  const prompt=mode==="adjust"
   ?`你是品牌视觉延展设计助手。只对当前方案做用户明确要求的局部调整，不推翻未被要求修改的结构。当前方案：${JSON.stringify(currentLayout)}。调整要求：${instruction}。品牌约束：${JSON.stringify(context)}。物料：${JSON.stringify(materials)}。只返回合法 JSON。`
   :`你是一名资深品牌视觉设计总监。任务不是分别做几张 Logo 放置图，而是先建立一个统一视觉系统，再把同一系统应用到全部物料。
必须遵守：
1. 不重新设计 Logo，不改变原始路径；优先继承 deconstructionStudy 的尺度、裁切、重复、负形和空间关系，再结合 deconstructionRoute 与 selectedExtensions 建立统一视觉语法。
2. 全部物料共享同一套网格、Logo 尺度策略、裁切规则、留白节奏、文字层级、色彩比例与信息密度。
3. 严格尊重每个物料的 width / height / unit，把它当真实画布比例。
4. material.withText=true 时建立 headline、subline、microcopy 信息层级并基于 material.copy 组织文案；material.withText=false 时三个文字字段都返回空字符串，让纯图形系统成为主体。
5. 允许超大尺度、边缘裁切、非对称网格、重复节奏，但必须服从当前路线；避免所有物料都变成 Logo 居中加左下小字。
6. 色彩严格服从 ratios 权重，不要逐张随机换色。
7. 先确定一个 system idea，再输出各物料参数；rationale 说明该物料如何继承统一系统。
8. 参考图只学习调性、留白、密度、信息层级与构图方法，不复制其中品牌元素。
品牌约束：${JSON.stringify(context)}。
物料与真实尺寸：${JSON.stringify(materials)}。
只返回合法 JSON。`;
  const schema={type:"object",additionalProperties:false,required:["layouts"],properties:{layouts:{type:"array",minItems:materials.length,maxItems:materials.length,items:layoutItem}}};

  if(apiMode==="chat"){
   const content:any[]=[{type:"text",text:`${prompt}\nJSON Schema：${JSON.stringify(schema)}`}];
   if(logoImage)content.push({type:"text",text:"原始 Logo 图形预览："},{type:"image_url",image_url:{url:logoImage}});
   for(const r of references){if(r.image)content.push({type:"text",text:`物料 ${r.id} 的用户参考图：`},{type:"image_url",image_url:{url:r.image}})}
   const url=`${base}/chat/completions`;
   const ai=await relayFetch(url,{method:"POST",headers:{"Authorization":`Bearer ${key}`,"Content-Type":"application/json"},body:JSON.stringify({model,messages:[{role:"system",content:"只输出合法 JSON，不要 Markdown。"},{role:"user",content}],temperature:0.5})});
   const data:any=await readResponse(ai);
   if(!ai.ok)return NextResponse.json({error:data?.error?.message||data?.message||data?.raw||`API 请求失败 (${ai.status})`},{status:ai.status});
   const text=data?.choices?.[0]?.message?.content;if(!text)return NextResponse.json({error:"中转 API 没有返回可用内容"},{status:502});
   try{return NextResponse.json(extractJson(text))}catch{return NextResponse.json({error:"模型返回内容不是有效 JSON，可尝试换模型或切换 Responses API。"},{status:502})}
  }

  const content:any[]=[{type:"input_text",text:prompt}];
  if(logoImage)content.push({type:"input_text",text:"下面是原始 Logo 图形预览："},{type:"input_image",image_url:logoImage,detail:"high"});
  for(const r of references){if(r.image)content.push({type:"input_text",text:`物料 ${r.id} 的用户参考图：`},{type:"input_image",image_url:r.image,detail:"high"})}
  const url=`${base}/responses`;
  const ai=await relayFetch(url,{method:"POST",headers:{"Authorization":`Bearer ${key}`,"Content-Type":"application/json"},body:JSON.stringify({model,store:false,input:[{role:"user",content}],text:{format:{type:"json_schema",name:"brand_layouts",strict:true,schema}}})});
  const data:any=await readResponse(ai);
  if(!ai.ok)return NextResponse.json({error:data?.error?.message||data?.message||data?.raw||`API 请求失败 (${ai.status})`},{status:ai.status});
  const text=data.output?.flatMap((x:any)=>x.content||[]).find((x:any)=>x.type==="output_text")?.text;
  if(!text)return NextResponse.json({error:"API 没有返回可用版式"},{status:502});
  return NextResponse.json(JSON.parse(text));
 }catch(e){return NextResponse.json({error:e instanceof Error?e.message:"服务端错误"},{status:500})}
}
