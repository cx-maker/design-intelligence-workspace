import { NextRequest, NextResponse } from "next/server";

const layoutItem = {
  type: "object", additionalProperties: false,
  required: ["materialId","concept","backgroundColor","logoScale","logoX","logoY","logoRotation","textPosition","textColor","rationale"],
  properties: {
    materialId:{type:"string"}, concept:{type:"string"}, backgroundColor:{type:"string"},
    logoScale:{type:"number",minimum:0.6,maximum:5}, logoX:{type:"number",minimum:-20,maximum:120},
    logoY:{type:"number",minimum:-20,maximum:120}, logoRotation:{type:"number",minimum:-45,maximum:45},
    textPosition:{type:"string",enum:["top-left","top-right","bottom-left","bottom-right"]}, textColor:{type:"string"}, rationale:{type:"string"}
  }
};

function safeBaseUrl(provider:string, raw?:string){
  if(provider==="openai") return "https://api.openai.com/v1";
  if(!raw) throw new Error("请填写中转 API Base URL");
  let url:URL; try{url=new URL(raw)}catch{throw new Error("Base URL 格式不正确")}
  if(url.protocol!=="https:") throw new Error("中转 API 仅允许 HTTPS 地址");
  const h=url.hostname.toLowerCase();
  const blocked=h==="localhost"||h==="0.0.0.0"||h==="::1"||/^127\./.test(h)||/^10\./.test(h)||/^192\.168\./.test(h)||/^169\.254\./.test(h)||/^172\.(1[6-9]|2\d|3[01])\./.test(h)||h.endsWith(".local")||h==="metadata.google.internal";
  if(blocked) throw new Error("该 Base URL 不允许使用");
  return url.toString().replace(/\/+$/,"");
}
function extractJson(text:string){return JSON.parse(text.trim().replace(/^```(?:json)?\s*/i,"").replace(/\s*```$/, ""))}

export async function POST(req:NextRequest){
  try{
    const key=req.headers.get("x-openai-key"); if(!key)return NextResponse.json({error:"请先配置 API Key"},{status:401});
    const body=await req.json();
    const {mode,model,provider="openai",baseUrl,apiMode="responses",logoImage,materials=[],references=[],context,currentLayout,instruction}=body;
    if(!model) return NextResponse.json({error:"请填写模型名"},{status:400});
    const base=safeBaseUrl(provider,baseUrl);

    if(mode==="test"){
      const url=apiMode==="chat"?`${base}/chat/completions`:`${base}/responses`;
      const payload=apiMode==="chat"?{model,messages:[{role:"user",content:"Reply only with OK"}],max_tokens:8,temperature:0}:{model,store:false,input:"Reply only with OK",max_output_tokens:8};
      const r=await fetch(url,{method:"POST",redirect:"error",headers:{"Authorization":`Bearer ${key}`,"Content-Type":"application/json"},body:JSON.stringify(payload)});
      const d=await r.json().catch(()=>({})); if(!r.ok)return NextResponse.json({error:d?.error?.message||`连接失败 (${r.status})`},{status:r.status});
      return NextResponse.json({ok:true,model,provider,apiMode});
    }

    const prompt=mode==="adjust"
      ?`你是品牌视觉延展设计助手。只对当前方案做用户明确要求的局部调整，不推翻未被要求修改的结构。当前方案：${JSON.stringify(currentLayout)}。调整要求：${instruction}。品牌约束：${JSON.stringify(context)}。物料：${JSON.stringify(materials)}。只返回合法 JSON。`
      :`你是品牌视觉延展设计助手。根据已经确定的 Logo 和用户约束，为每个物料生成克制、现代、国际化的二维品牌版式参数。不要重新设计 Logo，只决定原始 Logo 的比例、位置、裁切感、背景和信息位置。品牌约束：${JSON.stringify(context)}。物料：${JSON.stringify(materials)}。参考图只用于感知调性、留白、密度和构图，不复制其中品牌元素。只返回合法 JSON。`;
    const schema={type:"object",additionalProperties:false,required:["layouts"],properties:{layouts:{type:"array",minItems:materials.length,maxItems:materials.length,items:layoutItem}}};

    if(apiMode==="chat"){
      const content:any[]=[{type:"text",text:`${prompt}\nJSON Schema：${JSON.stringify(schema)}`}];
      if(logoImage)content.push({type:"text",text:"原始 Logo 图形预览："},{type:"image_url",image_url:{url:logoImage}});
      for(const r of references){if(r.image)content.push({type:"text",text:`物料 ${r.id} 的用户参考图：`},{type:"image_url",image_url:{url:r.image}})}
      const ai=await fetch(`${base}/chat/completions`,{method:"POST",redirect:"error",headers:{"Authorization":`Bearer ${key}`,"Content-Type":"application/json"},body:JSON.stringify({model,messages:[{role:"system",content:"只输出合法 JSON，不要 Markdown。"},{role:"user",content}],temperature:0.5})});
      const data=await ai.json().catch(()=>({})); if(!ai.ok)return NextResponse.json({error:data?.error?.message||`API 请求失败 (${ai.status})`},{status:ai.status});
      const text=data?.choices?.[0]?.message?.content; if(!text)return NextResponse.json({error:"中转 API 没有返回可用内容"},{status:502});
      try{return NextResponse.json(extractJson(text))}catch{return NextResponse.json({error:"模型返回内容不是有效 JSON，可尝试换模型或切换 Responses API。"},{status:502})}
    }

    const content:any[]=[{type:"input_text",text:prompt}];
    if(logoImage)content.push({type:"input_text",text:"下面是原始 Logo 图形预览："},{type:"input_image",image_url:logoImage,detail:"high"});
    for(const r of references){if(r.image)content.push({type:"input_text",text:`物料 ${r.id} 的用户参考图：`},{type:"input_image",image_url:r.image,detail:"high"})}
    const ai=await fetch(`${base}/responses`,{method:"POST",redirect:"error",headers:{"Authorization":`Bearer ${key}`,"Content-Type":"application/json"},body:JSON.stringify({model,store:false,input:[{role:"user",content}],text:{format:{type:"json_schema",name:"brand_layouts",strict:true,schema}}})});
    const data=await ai.json().catch(()=>({})); if(!ai.ok)return NextResponse.json({error:data?.error?.message||`API 请求失败 (${ai.status})`},{status:ai.status});
    const text=data.output?.flatMap((x:any)=>x.content||[]).find((x:any)=>x.type==="output_text")?.text;
    if(!text)return NextResponse.json({error:"API 没有返回可用版式"},{status:502});
    return NextResponse.json(JSON.parse(text));
  }catch(e){return NextResponse.json({error:e instanceof Error?e.message:"服务端错误"},{status:500})}
}
