const UUID=/^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
const services=new Set(['Solar, baterías y eólica','Electricidad y punto de recarga','Ahorro en factura y tarifas']);
const json=(body,status=200)=>new Response(JSON.stringify(body),{status,headers:{'Content-Type':'application/json','Cache-Control':'private, no-store','X-Content-Type-Options':'nosniff'}});
export function createHandler({database,keyHash,owner}) {
 return async request=>{
  try {
   const token=request.headers.get('Authorization')?.match(/^Bearer (.+)$/)?.[1]||'';
   if(token.length<40||token.length>100)return json({error:'Unauthorized'},401);
   const bytes=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(token));
   const actual=[...new Uint8Array(bytes)].map(x=>x.toString(16).padStart(2,'0')).join('');
   let diff=0;for(let i=0;i<64;i++)diff|=actual.charCodeAt(i)^keyHash.charCodeAt(i);
   if(diff)return json({error:'Unauthorized'},401);
   if(request.method!=='POST')return json({error:'Method not allowed'},405);
   const raw=await request.text();if(raw.length>18000)return json({error:'Too large'},413);
   const body=JSON.parse(raw);
   if(body.action==='probe'&&Object.keys(body).length===1){await database().unsafe('select 1 as ok');return json({ready:true});}
   if(Object.keys(body).some(k=>!['request_id','lead_id','lead','documents'].includes(k)))throw Error('Invalid fields');
   if(!UUID.test(body.request_id)||!UUID.test(body.lead_id))throw Error('Invalid reference');
   const lead=body.lead;
   if(!lead||Object.keys(lead).some(k=>!['name','contact','service','notes'].includes(k)))throw Error('Invalid lead');
   for(const [key,max] of [['name',100],['contact',25],['service',100],['notes',7000]])if(typeof lead[key]!=='string'||!lead[key].trim()||lead[key].length>max)throw Error('Invalid field');
   if(!services.has(lead.service)||!/^\+?[\d ().-]{9,25}$/.test(lead.contact))throw Error('Invalid service/contact');
   if(!Array.isArray(body.documents)||body.documents.length>3)throw Error('Invalid documents');
   const operations=[{entity:'leads',mode:'create',id:body.lead_id,data:{...lead,status:'new'}}];
   for(const doc of body.documents){
    const url=new URL(doc.url);
    if(typeof doc.title!=='string'||doc.title.length>120||url.protocol!=='https:'||url.username||url.password||!['www.romiluzenergiarenovable.com','romiluzenergiarenovable.com'].includes(url.hostname)||!/^\/asistente\/adjuntos\/\d+$/.test(url.pathname)||url.search||url.hash)throw Error('Invalid document');
    operations.push({entity:'documents',mode:'create',id:crypto.randomUUID(),data:{title:'Web '+body.lead_id+' · '+doc.title,kind:'web-assistant',storage_path:url.href,status:'pending'}});
   }
   // Reuses CONTROL's transactional audit/idempotency and fixes the owner in server code.
   const result=await database().unsafe('select public.romiluz_apply_changes($1::uuid,$2::uuid,$3::text::jsonb,$4::text,$5::text) as result',[owner,body.request_id,JSON.stringify(operations),'Nuevo cliente potencial de la web · Pendiente de contactar','assistant']);
   const saved=result?.[0]?.result?.results?.find(x=>x.entity==='leads')?.record;
   if(!saved||saved.id!==body.lead_id||saved.owner_id!==owner)throw Error('Not saved');
   return json({saved:true,lead_id:saved.id});
  } catch {return json({error:'No se ha podido registrar la solicitud.'},400);}
 };
}
