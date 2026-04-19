import { useState, useEffect, useRef, useCallback } from "react";
import { apiLogin, apiRegister, apiAnalyze, apiGetHistory, apiDeleteAnalysis } from "./api.js";

// ─── THEME ────────────────────────────────────────────────────────────────────
function useTheme() {
  const [dark, setDark] = useState(() => localStorage.getItem("vk_theme") !== "light");
  const toggle = () => setDark(d => { localStorage.setItem("vk_theme", d ? "light" : "dark"); return !d; });
  return { dark, toggle };
}

// ─── API imported from ./api.js ─────────────────────────────────────────────

// ─── ROUTER — persists login across reloads ───────────────────────────────────
function useRouter() {
  const [page, setPage] = useState(() => {
    const token = localStorage.getItem("vk_token");
    const user  = localStorage.getItem("vk_user");
    return (token && user) ? "dashboard" : "landing";
  });
  return { page, navigate: setPage };
}

// ─── ICONS ───────────────────────────────────────────────────────────────────
const I = {
  Menu:     () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/></svg>,
  X:        () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>,
  Upload:   () => <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>,
  Search:   () => <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>,
  History:  () => <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>,
  Image:    () => <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>,
  Plus:     () => <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>,
  ChevL:    () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="15 18 9 12 15 6"/></svg>,
  ChevR:    () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="9 18 15 12 9 6"/></svg>,
  ExtLink:  () => <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>,
  Pin:      () => <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>,
  Zap:      () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>,
  Brain:    () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96-.46 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 1.98-3A2.5 2.5 0 0 1 9.5 2Z"/><path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96-.46 2.5 2.5 0 0 0 2.96-3.08 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-1.98-3A2.5 2.5 0 0 0 14.5 2Z"/></svg>,
  LogOut:   () => <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>,
  Mail:     () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22 6 12 13 2 6"/></svg>,
  Sun:      () => <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>,
  Moon:     () => <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>,
  ImgErr:   () => <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/><line x1="2" y1="2" x2="22" y2="22" strokeDasharray="3 2" opacity="0.4"/></svg>,
};

// ─── CSS ──────────────────────────────────────────────────────────────────────
const makeCSS = (dark) => `
  @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=Crimson+Pro:ital,wght@0,300;0,400;0,600;1,400&family=JetBrains+Mono:wght@300;400;500&display=swap');
  *{box-sizing:border-box;margin:0;padding:0;}
  :root{
    --bg:      ${dark?"#050810":"#f4f0e6"};
    --bg-mid:  ${dark?"#080d1a":"#eae4d4"};
    --bg-card: ${dark?"#0c1222":"#faf7f0"};
    --bg-h:    ${dark?"#111828":"#e0d8c4"};
    --bdr:     ${dark?"#1a2540":"#cfc3a0"};
    --bdr-b:   ${dark?"#2a3a5c":"#b0a070"};
    --gold:    ${dark?"#c9a84c":"#a07020"};
    --gd:      ${dark?"#8a6e2f":"#c9a84c"};
    --teal:    ${dark?"#0d9488":"#0a6858"};
    --td:      ${dark?"#0a5c56":"#0d9488"};
    --tp:      ${dark?"#e8e4d8":"#1a1206"};
    --ts:      ${dark?"#8a9bb5":"#5a4a30"};
    --tdim:    ${dark?"#4a5568":"#9a8a60"};
  }
  body{background:var(--bg);color:var(--tp);font-family:'Crimson Pro',Georgia,serif;min-height:100vh;overflow-x:hidden;transition:background .3s,color .3s;}
  .fd{font-family:'Cinzel',serif;}
  .fm{font-family:'JetBrains Mono',monospace;}
  ::-webkit-scrollbar{width:4px;height:4px;}
  ::-webkit-scrollbar-track{background:var(--bg);}
  ::-webkit-scrollbar-thumb{background:var(--bdr-b);border-radius:2px;}
  @keyframes fiu{from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:translateY(0)}}
  @keyframes fi{from{opacity:0}to{opacity:1}}
  @keyframes shim{0%{background-position:-200% center}100%{background-position:200% center}}
  @keyframes sp{from{transform:rotate(0)}to{transform:rotate(360deg)}}
  @keyframes gpulse{0%,100%{opacity:.4}50%{opacity:1}}
  @keyframes spslow{from{transform:rotate(0)}to{transform:rotate(360deg)}}
  .afu{animation:fiu .6s ease forwards;}
  .afi{animation:fi .4s ease forwards;}
  .aspslow{animation:spslow 20s linear infinite;}
  .tgg{background:linear-gradient(135deg,#c9a84c 0%,#e8c97a 40%,#c9a84c 70%,#8a6e2f 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;background-size:200% auto;animation:shim 4s linear infinite;}
  .gbg{background-image:linear-gradient(var(--bdr) 1px,transparent 1px),linear-gradient(90deg,var(--bdr) 1px,transparent 1px);background-size:40px 40px;}
  .card{background:var(--bg-card);border:1px solid var(--bdr);border-radius:8px;transition:border-color .2s,box-shadow .2s;}
  .card:hover{border-color:var(--bdr-b);}
  .cardg{border-color:var(--gd);}
  .cardg:hover{border-color:var(--gold);box-shadow:0 0 20px rgba(201,168,76,.07);}
  .bng{background:linear-gradient(135deg,#c9a84c,#8a6e2f);color:${dark?"#050810":"#fff"};font-family:'Cinzel',serif;font-weight:600;letter-spacing:.08em;border:none;cursor:pointer;transition:all .2s;border-radius:4px;}
  .bng:hover{background:linear-gradient(135deg,#e8c97a,#c9a84c);transform:translateY(-1px);box-shadow:0 4px 20px rgba(201,168,76,.3);}
  .bng:disabled{opacity:.6;cursor:not-allowed;transform:none;}
  .bno{background:transparent;color:var(--gold);font-family:'Cinzel',serif;font-weight:600;letter-spacing:.08em;border:1px solid var(--gd);cursor:pointer;transition:all .2s;border-radius:4px;}
  .bno:hover{border-color:var(--gold);background:rgba(201,168,76,.05);}
  .inp{background:var(--bg-mid);border:1px solid var(--bdr);border-radius:6px;color:var(--tp);font-family:'Crimson Pro',serif;font-size:16px;padding:12px 16px;width:100%;transition:border-color .2s,box-shadow .2s;outline:none;}
  .inp:focus{border-color:var(--gd);box-shadow:0 0 0 2px rgba(201,168,76,.1);}
  .inp::placeholder{color:var(--tdim);}
  .sidebar{transition:width .3s cubic-bezier(.4,0,.2,1);overflow:hidden;}
  .gdot{width:6px;height:6px;border-radius:50%;background:var(--gold);box-shadow:0 0 8px var(--gold);animation:gpulse 2s ease-in-out infinite;display:inline-block;}
  .thbtn{background:var(--bg-mid);border:1px solid var(--bdr);border-radius:20px;padding:5px 11px;cursor:pointer;color:var(--ts);display:flex;align-items:center;gap:5px;transition:all .2s;font-size:11px;}
  .thbtn:hover{border-color:var(--gd);color:var(--gold);}
  .spin{width:16px;height:16px;border:2px solid rgba(255,255,255,.2);border-top-color:currentColor;border-radius:50%;animation:sp .7s linear infinite;display:inline-block;}
  .errbox{background:rgba(239,68,68,.08);border:1px solid rgba(239,68,68,.3);border-radius:8px;padding:14px 18px;color:#ef4444;font-size:14px;margin-top:14px;}
  .tab-btn{padding:8px 16px;border-radius:4px;cursor:pointer;font-family:'Cinzel',serif;font-size:13px;letter-spacing:.07em;transition:all .15s;border:1px solid transparent;}
  .tab-btn.active{background:rgba(201,168,76,.1);border-color:var(--gd);color:var(--gold);}
  .tab-btn:not(.active){background:none;color:var(--ts);}
  .tab-btn:not(.active):hover{color:var(--tp);}
  .meta-row{display:flex;flex-wrap:wrap;gap:6px 24px;margin-top:14px;}
  .meta-item{font-size:14px;color:var(--ts);}
  .meta-item span{color:var(--tdim);font-size:13px;}
  .img-card{border-radius:10px;overflow:hidden;border:1px solid var(--bdr);cursor:pointer;transition:border-color .2s,transform .2s;}
  .img-card:hover{border-color:var(--gold);transform:scale(1.02);}
  .img-card img{width:100%;height:200px;object-fit:cover;display:block;background:var(--bg-mid);}
  .img-placeholder{width:100%;height:200px;display:flex;align-items:center;justify-content:center;background:var(--bg-mid);color:var(--tdim);}
  .modal-overlay{position:fixed;inset:0;background:rgba(0,0,0,.85);z-index:1000;display:flex;align-items:center;justify-content:center;padding:24px;}
  .modal-img{max-width:90vw;max-height:85vh;object-fit:contain;border-radius:8px;}
`;

// ─── SHARED COMPONENTS ────────────────────────────────────────────────────────
function Logo({ onClick }) {
  return (
    <button onClick={onClick} style={{background:"none",border:"none",cursor:"pointer",display:"flex",alignItems:"center",gap:10}}>
      <div style={{width:32,height:32,position:"relative"}}>
        <div style={{width:32,height:32,border:"1.5px solid #c9a84c",borderRadius:"50%",display:"flex",alignItems:"center",justifyContent:"center"}}>
          <div style={{width:12,height:12,background:"linear-gradient(135deg,#c9a84c,#8a6e2f)",borderRadius:"50%"}}/>
        </div>
        <div style={{position:"absolute",top:"50%",left:"50%",transform:"translate(-50%,-50%) rotate(45deg)",width:22,height:22,border:"1px solid rgba(201,168,76,.4)",borderRadius:2}}/>
      </div>
      <span className="fd" style={{fontSize:15,letterSpacing:"0.1em",color:"#c9a84c"}}>VISHWAKARMA AI</span>
    </button>
  );
}

function ThemeToggle({ dark, toggle }) {
  return (
    <button className="thbtn" onClick={toggle} title={dark?"Light mode":"Dark mode"}>
      {dark ? <I.Sun/> : <I.Moon/>}
      <span className="fm" style={{letterSpacing:"0.1em"}}>{dark?"LIGHT":"DARK"}</span>
    </button>
  );
}

// Badge pill
function Badge({ children, color = "gold" }) {
  const c = color === "teal"
    ? { bg:"rgba(13,148,136,.12)", border:"var(--td)", text:"var(--teal)" }
    : { bg:"rgba(201,168,76,.12)", border:"var(--gd)", text:"var(--gold)" };
  return (
    <span style={{background:c.bg,border:`1px solid ${c.border}`,borderRadius:4,padding:"3px 11px",fontSize:13,color:c.text,fontFamily:"'Cinzel',serif",whiteSpace:"nowrap"}}>{children}</span>
  );
}

// ─── LANDING PAGE ─────────────────────────────────────────────────────────────
function LandingPage({ navigate, dark, toggle }) {
  const [sy, setSy] = useState(0);
  useEffect(() => { const h=()=>setSy(window.scrollY); window.addEventListener("scroll",h); return()=>window.removeEventListener("scroll",h); },[]);
  return (
    <div style={{minHeight:"100vh",background:"var(--bg)"}}>
      <header style={{position:"fixed",top:0,left:0,right:0,zIndex:100,padding:"16px 40px",display:"flex",alignItems:"center",justifyContent:"space-between",borderBottom:sy>40?"1px solid var(--bdr)":"1px solid transparent",background:sy>40?"var(--bg-mid)":"transparent",backdropFilter:sy>40?"blur(12px)":"none",transition:"all .3s"}}>
        <Logo onClick={()=>{}}/>
        <div style={{display:"flex",gap:10,alignItems:"center"}}>
          <ThemeToggle dark={dark} toggle={toggle}/>
          <button className="bno" style={{padding:"8px 20px",fontSize:13}} onClick={()=>navigate("about")}>About</button>
          <button className="bng" style={{padding:"8px 20px",fontSize:13}} onClick={()=>navigate("login")}>Login</button>
        </div>
      </header>

      {/* Hero */}
      <section style={{minHeight:"100vh",display:"flex",flexDirection:"column",alignItems:"center",justifyContent:"center",position:"relative",overflow:"hidden",padding:"120px 40px 80px"}}>
        <div className="gbg" style={{position:"absolute",inset:0,opacity:.3}}/>
        <div style={{position:"absolute",top:"50%",left:"50%",transform:"translate(-50%,-50%)",width:600,height:600,background:"radial-gradient(ellipse,rgba(201,168,76,.06) 0%,transparent 70%)",pointerEvents:"none"}}/>
        <div className="aspslow" style={{position:"absolute",top:"50%",left:"50%",transform:"translate(-50%,-50%)",width:480,height:480,border:"1px solid rgba(201,168,76,.06)",borderRadius:"50%",pointerEvents:"none"}}/>

        <div style={{textAlign:"center",position:"relative",zIndex:2,maxWidth:800}}>
          <div style={{display:"inline-flex",alignItems:"center",gap:8,background:"rgba(201,168,76,.08)",border:"1px solid rgba(201,168,76,.2)",borderRadius:100,padding:"6px 16px",marginBottom:32}}>
            <span className="gdot"/>
            <span className="fm" style={{fontSize:11,color:"var(--gold)",letterSpacing:"0.15em"}}>ARCHITECTURAL INTELLIGENCE SYSTEM v2.4</span>
          </div>
          <h1 className="fd afu" style={{fontSize:"clamp(36px,6vw,72px)",lineHeight:1.1,marginBottom:24,letterSpacing:"-0.02em"}}>
            <span className="tgg">Decode the Sacred</span><br/>
            <span style={{color:"var(--tp)"}}>Architecture of</span><br/>
            <span style={{color:"var(--ts)"}}>India</span>
          </h1>
          <p className="afu" style={{fontSize:20,color:"var(--ts)",lineHeight:1.7,margin:"0 auto 48px",maxWidth:560,animationDelay:".15s"}}>
            AI-powered recognition of Dravidian, Chola, Hoysala, Vijayanagara, Mughal and more — from a single photograph.
          </p>
          <div style={{display:"flex",gap:16,justifyContent:"center",flexWrap:"wrap"}}>
            <button className="bng afu" style={{padding:"14px 36px",fontSize:14,animationDelay:".3s"}} onClick={()=>navigate("register")}>Get Started</button>
            <button className="bno afu" style={{padding:"14px 36px",fontSize:14,animationDelay:".4s"}} onClick={()=>navigate("about")}>Learn More</button>
          </div>
        </div>
      </section>

      {/* Steps */}
      <section style={{padding:"100px 40px",maxWidth:1100,margin:"0 auto"}}>
        <div style={{textAlign:"center",marginBottom:72}}>
          <div className="fm" style={{fontSize:11,color:"var(--gold)",letterSpacing:"0.2em",marginBottom:16}}>PROCESS</div>
          <h2 className="fd" style={{fontSize:"clamp(24px,4vw,40px)",marginBottom:16}}>How It Works</h2>
          <div style={{width:60,height:1,background:"var(--gd)",margin:"0 auto"}}/>
        </div>
        <div style={{display:"grid",gridTemplateColumns:"1fr auto 1fr auto 1fr",gap:0,alignItems:"center"}}>
          {[{num:"01",icon:<I.Zap/>,title:"Login",desc:"Create your account to access the analysis platform."},{num:"02",icon:<I.Upload/>,title:"Upload Image",desc:"Drop any photograph of an Indian monument or temple."},{num:"03",icon:<I.Brain/>,title:"AI Analysis",desc:"Get architectural style, era, builder, and description instantly."}].map((s,i)=>(
            <>
              <div key={i} className="card cardg" style={{padding:"32px 28px",textAlign:"center"}}>
                <div style={{width:48,height:48,borderRadius:"50%",background:"rgba(201,168,76,.1)",border:"1px solid var(--gd)",display:"flex",alignItems:"center",justifyContent:"center",margin:"0 auto 20px",color:"var(--gold)"}}>{s.icon}</div>
                <div className="fm" style={{fontSize:11,color:"var(--gd)",letterSpacing:"0.2em",marginBottom:12}}>{s.num}</div>
                <h3 className="fd" style={{fontSize:18,marginBottom:12}}>{s.title}</h3>
                <p style={{fontSize:15,color:"var(--ts)",lineHeight:1.6}}>{s.desc}</p>
              </div>
              {i<2&&<div key={`d${i}`} style={{padding:"0 16px",display:"flex",flexDirection:"column",alignItems:"center",gap:4}}><div style={{width:40,height:1,background:"linear-gradient(to right,var(--gd),transparent)"}}/><div style={{width:6,height:6,borderRadius:"50%",background:"var(--gd)"}}/><div style={{width:40,height:1,background:"linear-gradient(to left,var(--gd),transparent)"}}/></div>}
            </>
          ))}
        </div>
      </section>

      {/* Styles */}
      <section style={{padding:"80px 40px",background:"var(--bg-mid)",borderTop:"1px solid var(--bdr)",borderBottom:"1px solid var(--bdr)"}}>
        <div style={{maxWidth:1100,margin:"0 auto"}}>
          <div style={{textAlign:"center",marginBottom:56}}>
            <div className="fm" style={{fontSize:11,color:"var(--gold)",letterSpacing:"0.2em",marginBottom:16}}>DETECTABLE STYLES</div>
            <h2 className="fd" style={{fontSize:"clamp(22px,3vw,36px)"}}>Great Architectural Traditions</h2>
          </div>
          <div style={{display:"grid",gridTemplateColumns:"repeat(auto-fit,minmax(120px,1fr))",gap:16}}>
            {["Dravidian","Chola","Hoysala","Vijayanagara","Nayaka","Mughal","Rajput","Buddhist","Pallava","Chalukya"].map((s,i)=>(
              <div key={s} style={{textAlign:"center",padding:"20px 12px",border:"1px solid var(--bdr)",borderRadius:8,background:"var(--bg-card)"}}>
                <div style={{width:38,height:38,borderRadius:"50%",background:`hsl(${40+i*15},55%,${25+i*2}%)`,border:"1px solid var(--gd)",margin:"0 auto 14px",display:"flex",alignItems:"center",justifyContent:"center"}}>
                  <span className="fd" style={{fontSize:13,color:"var(--gold)"}}>{s[0]}</span>
                </div>
                <div className="fd" style={{fontSize:12,letterSpacing:"0.04em",color:"var(--tp)"}}>{s}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <footer style={{padding:"40px",borderTop:"1px solid var(--bdr)"}}>
        <div style={{maxWidth:1100,margin:"0 auto",display:"flex",alignItems:"center",justifyContent:"space-between",flexWrap:"wrap",gap:20}}>
          <Logo onClick={()=>{}}/>
          <div style={{display:"flex",gap:28}}>
            {[["about","About Us"],["contact","Contact"]].map(([p,l])=>(
              <button key={p} onClick={()=>navigate(p)} style={{background:"none",border:"none",color:"var(--ts)",cursor:"pointer",fontSize:14,fontFamily:"'Crimson Pro',serif"}}>{l}</button>
            ))}
          </div>
          <div className="fm" style={{fontSize:11,color:"var(--tdim)",letterSpacing:"0.1em"}}>© 2024 VISHWAKARMA AI</div>
        </div>
      </footer>
    </div>
  );
}

// ─── AUTH PAGE ────────────────────────────────────────────────────────────────
function AuthPage({ mode, navigate, dark, toggle }) {
  const [form, setForm] = useState({name:"",email:"",password:""});
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState(null);
  const isLogin = mode==="login";
  const submit = async () => {
    if (!form.email||!form.password) return;
    setLoading(true);
    try {
      const data = isLogin
        ? await apiLogin(form.email, form.password)
        : await apiRegister(form.name, form.email, form.password);
      localStorage.setItem("vk_token", data.access_token);
      localStorage.setItem("vk_user", JSON.stringify(data.user));
      navigate("dashboard");
    } catch(e) {
      setErr(e.message || "Authentication failed");
    } finally {
      setLoading(false);
    }
  };
  return (
    <div style={{minHeight:"100vh",display:"flex",alignItems:"center",justifyContent:"center",position:"relative",padding:24}}>
      <div className="gbg" style={{position:"absolute",inset:0,opacity:.2}}/>
      <div style={{position:"absolute",top:24,left:40}}><Logo onClick={()=>navigate("landing")}/></div>
      <div style={{position:"absolute",top:24,right:40}}><ThemeToggle dark={dark} toggle={toggle}/></div>
      <div className="card cardg afu" style={{width:"100%",maxWidth:440,padding:"48px 40px",position:"relative",zIndex:2}}>
        <div style={{textAlign:"center",marginBottom:40}}>
          <div className="fm" style={{fontSize:11,color:"var(--gold)",letterSpacing:"0.2em",marginBottom:12}}>{isLogin?"WELCOME BACK":"JOIN THE PLATFORM"}</div>
          <h2 className="fd" style={{fontSize:28}}>{isLogin?"Sign In":"Create Account"}</h2>
        </div>
        <div style={{display:"flex",flexDirection:"column",gap:16}}>
          {!isLogin&&<div><label style={{display:"block",fontSize:13,color:"var(--ts)",marginBottom:8,fontFamily:"'Cinzel',serif",letterSpacing:"0.1em"}}>FULL NAME</label><input className="inp" placeholder="Your name" value={form.name} onChange={e=>setForm({...form,name:e.target.value})}/></div>}
          <div><label style={{display:"block",fontSize:13,color:"var(--ts)",marginBottom:8,fontFamily:"'Cinzel',serif",letterSpacing:"0.1em"}}>EMAIL</label><input className="inp" type="email" placeholder="you@example.com" value={form.email} onChange={e=>setForm({...form,email:e.target.value})}/></div>
          <div><label style={{display:"block",fontSize:13,color:"var(--ts)",marginBottom:8,fontFamily:"'Cinzel',serif",letterSpacing:"0.1em"}}>PASSWORD</label><input className="inp" type="password" placeholder="••••••••" value={form.password} onChange={e=>setForm({...form,password:e.target.value})}/></div>
          {err&&<div className="errbox">⚠ {err}</div>}
          <button className="bng" style={{padding:"14px",fontSize:14,marginTop:8,width:"100%"}} onClick={submit} disabled={loading}>
            {loading?<span style={{display:"flex",alignItems:"center",justifyContent:"center",gap:8}}><span className="spin"/>Authenticating...</span>:isLogin?"Sign In":"Create Account"}
          </button>
        </div>
        <div style={{textAlign:"center",marginTop:28,fontSize:15,color:"var(--ts)"}}>
          {isLogin?"Don't have an account? ":"Already have an account? "}
          <button onClick={()=>navigate(isLogin?"register":"login")} style={{background:"none",border:"none",color:"var(--gold)",cursor:"pointer",fontSize:15,fontFamily:"'Crimson Pro',serif",textDecoration:"underline"}}>{isLogin?"Register":"Sign In"}</button>
        </div>
      </div>
    </div>
  );
}

// ─── SIDEBAR ──────────────────────────────────────────────────────────────────
function Sidebar({ open, setOpen, navigate, history, onPick, onLogout }) {
  return (
    <div className="sidebar" style={{width:open?240:60,background:"var(--bg-mid)",borderRight:"1px solid var(--bdr)",display:"flex",flexDirection:"column",flexShrink:0,height:"100vh",position:"sticky",top:0}}>
      <div style={{padding:"16px 12px",borderBottom:"1px solid var(--bdr)",display:"flex",alignItems:"center",justifyContent:open?"space-between":"center"}}>
        {open&&<span className="fd" style={{fontSize:12,color:"var(--gold)",letterSpacing:"0.1em",whiteSpace:"nowrap"}}>MENU</span>}
        <button onClick={()=>setOpen(!open)} style={{background:"none",border:"none",color:"var(--ts)",cursor:"pointer",padding:4,borderRadius:4,display:"flex"}}>{open?<I.X/>:<I.Menu/>}</button>
      </div>
      <div style={{padding:"12px 8px",flex:1,overflowY:"auto"}}>
        {[{icon:<I.Plus/>,label:"New Analysis",to:"upload"},{icon:<I.Image/>,label:"Upload Image",to:"upload"},{icon:<I.History/>,label:"History",to:null}].map((it,i)=>(
          <button key={i} onClick={()=>it.to&&navigate(it.to)} style={{width:"100%",display:"flex",alignItems:"center",gap:12,padding:"10px 8px",background:"none",border:"none",color:"var(--ts)",cursor:"pointer",borderRadius:6,transition:"all .15s",whiteSpace:"nowrap",overflow:"hidden"}}
            onMouseEnter={e=>{e.currentTarget.style.background="var(--bg-h)";e.currentTarget.style.color="var(--tp)";}}
            onMouseLeave={e=>{e.currentTarget.style.background="none";e.currentTarget.style.color="var(--ts)";}}>
            <span style={{flexShrink:0}}>{it.icon}</span>
            {open&&<span style={{fontSize:14}}>{it.label}</span>}
          </button>
        ))}
        {open&&history.length>0&&(
          <div style={{marginTop:24}}>
            <div className="fm" style={{fontSize:10,color:"var(--tdim)",letterSpacing:"0.15em",padding:"0 8px",marginBottom:8}}>RECENT</div>
            {history.map((h,i)=>(
              <button key={i} onClick={()=>onPick(h)} style={{width:"100%",padding:"8px 8px",background:"none",border:"none",textAlign:"left",cursor:"pointer",borderRadius:6}}
                onMouseEnter={e=>e.currentTarget.style.background="var(--bg-h)"}
                onMouseLeave={e=>e.currentTarget.style.background="none"}>
                <div style={{fontSize:12,color:"var(--tp)",whiteSpace:"nowrap",overflow:"hidden",textOverflow:"ellipsis"}}>{h.monument_name||h.name}</div>
                <div className="fm" style={{fontSize:10,color:"var(--tdim)",marginTop:2}}>{h.style} · {h.built}</div>
              </button>
            ))}
          </div>
        )}
      </div>
      <div style={{padding:"12px 8px",borderTop:"1px solid var(--bdr)"}}>
        <button onClick={()=>onLogout&&onLogout()} style={{width:"100%",display:"flex",alignItems:"center",gap:12,padding:"10px 8px",background:"none",border:"none",color:"var(--ts)",cursor:"pointer",borderRadius:6,whiteSpace:"nowrap",overflow:"hidden"}}>
          <span style={{flexShrink:0}}><I.LogOut/></span>
          {open&&<span style={{fontSize:14}}>Sign Out</span>}
        </button>
      </div>
    </div>
  );
}

// ─── DASHBOARD ────────────────────────────────────────────────────────────────
function Dashboard({ navigate, history, setAnalysis, onLogout, dark, toggle }) {
  const [open, setOpen] = useState(false);
  const [drag, setDrag] = useState(false);
  const [preview, setPreview] = useState(null);
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState(null);
  const ref = useRef();

  const handleFile = f => { if(!f) return; setFile(f); setErr(null); const r=new FileReader(); r.onload=e=>setPreview(e.target.result); r.readAsDataURL(f); };
  const analyze = async () => {
    if(!file) return;
    setLoading(true); setErr(null);
    try {
      const d = await apiAnalyze(file);
      // Normalise field names from FastAPI response
      const norm = {
        ...d,
        name: d.monument_name || d.name,
      };
      setAnalysis(norm);
      navigate("analysis");
    }
    catch(e) { setErr(e.message||"Analysis failed."); }
    finally { setLoading(false); }
  };

  return (
    <div style={{display:"flex",minHeight:"100vh"}}>
      <Sidebar open={open} setOpen={setOpen} navigate={navigate} history={history} onPick={h=>{setAnalysis(h);navigate("analysis");}} onLogout={onLogout}/>
      <div style={{flex:1,overflow:"auto"}}>
        {/* Topbar */}
        <div style={{padding:"16px 32px",borderBottom:"1px solid var(--bdr)",display:"flex",alignItems:"center",justifyContent:"space-between",background:"var(--bg-mid)",position:"sticky",top:0,zIndex:10}}>
          <div>
            <h1 className="fd" style={{fontSize:20,letterSpacing:"0.05em"}}>Analysis Dashboard</h1>
            <div className="fm" style={{fontSize:11,color:"var(--ts)",marginTop:2}}>Upload a monument photo for AI-powered architectural analysis</div>
          </div>
          <div style={{display:"flex",alignItems:"center",gap:12}}>
            <ThemeToggle dark={dark} toggle={toggle}/>
            <span className="gdot"/><span className="fm" style={{fontSize:11,color:"var(--gold)"}}>SYSTEM ONLINE</span>
          </div>
        </div>

        <div style={{maxWidth:800,margin:"0 auto",padding:"60px 32px"}}>
          {/* Drop zone */}
          <div
            onDragOver={e=>{e.preventDefault();setDrag(true);}}
            onDragLeave={()=>setDrag(false)}
            onDrop={e=>{e.preventDefault();setDrag(false);handleFile(e.dataTransfer.files[0]);}}
            onClick={()=>!preview&&ref.current.click()}
            style={{border:`2px dashed ${drag?"var(--gold)":preview?"var(--gd)":"var(--bdr-b)"}`,borderRadius:12,padding:preview?0:"80px 40px",textAlign:"center",cursor:preview?"default":"pointer",background:drag?"rgba(201,168,76,.04)":"var(--bg-card)",transition:"all .2s",overflow:"hidden"}}>
            <input ref={ref} type="file" accept="image/*" style={{display:"none"}} onChange={e=>handleFile(e.target.files[0])}/>
            {preview?(
              <div>
                <img src={preview} alt="preview" style={{width:"100%",maxHeight:400,objectFit:"cover",display:"block"}}/>
                <div style={{padding:"16px 24px",display:"flex",alignItems:"center",justifyContent:"space-between",background:"var(--bg-mid)"}}>
                  <span style={{fontSize:14,color:"var(--ts)"}}>Image ready for analysis</span>
                  <button onClick={e=>{e.stopPropagation();setPreview(null);setFile(null);setErr(null);}} style={{background:"none",border:"1px solid var(--bdr)",color:"var(--ts)",cursor:"pointer",padding:"5px 12px",borderRadius:4,fontSize:12}}>Remove</button>
                </div>
              </div>
            ):(
              <div>
                <div style={{width:64,height:64,borderRadius:"50%",background:"rgba(201,168,76,.08)",border:"1px solid var(--gd)",display:"flex",alignItems:"center",justifyContent:"center",margin:"0 auto 24px",color:"var(--gold)"}}><I.Upload/></div>
                <h3 className="fd" style={{fontSize:20,marginBottom:12}}>Drop Your Image Here</h3>
                <p style={{color:"var(--ts)",fontSize:16,marginBottom:24}}>Drag and drop a monument photograph, or click to browse</p>
                <div className="fm" style={{fontSize:11,color:"var(--tdim)",letterSpacing:"0.1em"}}>SUPPORTS: JPG · PNG · WEBP · HEIC</div>
              </div>
            )}
          </div>

          {err&&<div className="errbox">⚠ {err}</div>}

          {preview&&(
            <div style={{marginTop:24,textAlign:"center"}}>
              <button className="bng" style={{padding:"16px 64px",fontSize:14}} onClick={analyze} disabled={loading}>
                {loading?<span style={{display:"flex",alignItems:"center",gap:10}}><span className="spin"/>Analyzing Architecture...</span>
                        :<span style={{display:"flex",alignItems:"center",gap:8}}><I.Search/>Analyze Monument</span>}
              </button>
            </div>
          )}

          {/* History grid */}
          {history.length>0&&(
            <div style={{marginTop:64}}>
              <div style={{display:"flex",alignItems:"center",justifyContent:"space-between",marginBottom:24}}>
                <h2 className="fd" style={{fontSize:18,letterSpacing:"0.05em"}}>Recent Analyses</h2>
                <span className="fm" style={{fontSize:11,color:"var(--tdim)"}}>{history.length} RESULTS</span>
              </div>
              <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:16}}>
                {history.map((h,i)=>(
                  <button key={i} className="card" style={{padding:"20px",textAlign:"left",cursor:"pointer",border:"1px solid var(--bdr)",background:"none",width:"100%",transition:"all .15s"}}
                    onClick={()=>{setAnalysis(h);navigate("analysis");}}
                    onMouseEnter={e=>{e.currentTarget.style.borderColor="var(--gd)";e.currentTarget.style.background="var(--bg-h)";}}
                    onMouseLeave={e=>{e.currentTarget.style.borderColor="var(--bdr)";e.currentTarget.style.background="none";}}>
                    <div style={{display:"flex",alignItems:"flex-start",justifyContent:"space-between",marginBottom:10}}>
                      <div>
                        <div style={{fontSize:15,color:"var(--tp)",fontWeight:600,fontFamily:"'Cinzel',serif"}}>{h.monument_name||h.name}</div>
                        <div style={{fontSize:13,color:"var(--ts)",marginTop:3}}>{h.style} Architecture</div>
                      </div>
                      <Badge>{h.architecture?.split("(")[0].trim()||h.style}</Badge>
                    </div>
                    <div className="fm" style={{fontSize:11,color:"var(--tdim)"}}>{h.location}</div>
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// ─── IMAGE MODAL ──────────────────────────────────────────────────────────────
function ImgModal({ url, caption, onClose }) {
  useEffect(()=>{ const h=e=>{if(e.key==="Escape")onClose();}; window.addEventListener("keydown",h); return()=>window.removeEventListener("keydown",h); },[]);
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div onClick={e=>e.stopPropagation()} style={{display:"flex",flexDirection:"column",alignItems:"center",gap:12,maxWidth:"90vw"}}>
        <img src={url} alt={caption} className="modal-img" onError={e=>e.target.style.display="none"}/>
        {caption&&<div className="fm" style={{fontSize:12,color:"rgba(255,255,255,.6)",letterSpacing:"0.1em",textAlign:"center"}}>{caption}</div>}
        <button onClick={onClose} style={{background:"rgba(255,255,255,.1)",border:"1px solid rgba(255,255,255,.2)",color:"#fff",padding:"6px 20px",borderRadius:4,cursor:"pointer",fontSize:13}}>Close</button>
      </div>
    </div>
  );
}

// ─── ANALYSIS PAGE ────────────────────────────────────────────────────────────
function AnalysisPage({ navigate, analysis, history, setAnalysis, onLogout, dark, toggle }) {
  const [sopen, setSopen] = useState(false);
  const [tab, setTab] = useState("details");
  const [modal, setModal] = useState(null);

  if(!analysis) return (
    <div style={{minHeight:"100vh",display:"flex",alignItems:"center",justifyContent:"center"}}>
      <div style={{textAlign:"center"}}>
        <p style={{color:"var(--ts)",marginBottom:16}}>No analysis loaded. Upload an image first.</p>
        <button className="bng" style={{padding:"10px 24px",fontSize:13}} onClick={()=>navigate("dashboard")}>Go to Dashboard</button>
      </div>
    </div>
  );

  const TABS = ["details","images","analysis","sources"];
  const gallery = analysis.gallery||[];
  const probs = analysis.probabilities||{};

  return (
    <div style={{display:"flex",minHeight:"100vh"}}>
      <Sidebar open={sopen} setOpen={setSopen} navigate={navigate} history={history} onPick={h=>{setAnalysis(h);setTab("details");}} onLogout={onLogout}/>

      <div style={{flex:1,overflow:"auto"}}>
        {/* Topbar */}
        <div style={{position:"sticky",top:0,zIndex:10,background:"var(--bg-mid)",backdropFilter:"blur(12px)",borderBottom:"1px solid var(--bdr)",padding:"0 28px",display:"flex",alignItems:"center",justifyContent:"space-between",height:56,gap:12,flexWrap:"wrap"}}>
          <div style={{display:"flex",alignItems:"center",gap:8}}>
            <button onClick={()=>navigate("dashboard")} style={{background:"none",border:"none",color:"var(--ts)",cursor:"pointer",display:"flex",alignItems:"center",gap:4,fontSize:14,padding:"4px 8px"}}><I.ChevL/>Back</button>
            <span style={{color:"var(--bdr-b)"}}>·</span>
            <span className="fm" style={{fontSize:12,color:"var(--ts)",overflow:"hidden",textOverflow:"ellipsis",whiteSpace:"nowrap",maxWidth:200}}>{analysis.name}</span>
          </div>
          <div style={{display:"flex",gap:4,alignItems:"center",flexWrap:"wrap"}}>
            <ThemeToggle dark={dark} toggle={toggle}/>
            {TABS.map(t=>(
              <button key={t} className={`tab-btn${tab===t?" active":""}`} onClick={()=>setTab(t)}>
                {t.charAt(0).toUpperCase()+t.slice(1)}
              </button>
            ))}
          </div>
        </div>

        <div style={{maxWidth:960,margin:"0 auto",padding:"40px 28px"}}>

          {/* ── DETAILS TAB ── */}
          {tab==="details"&&(
            <div className="afi">
              {/* Header card */}
              <div className="card cardg" style={{padding:"36px 40px",marginBottom:28,position:"relative",overflow:"hidden"}}>
                <div style={{position:"absolute",top:0,right:0,width:200,height:200,background:"radial-gradient(circle at 100% 0%,rgba(201,168,76,.06) 0%,transparent 60%)"}}/>
                <div style={{display:"flex",alignItems:"flex-start",justifyContent:"space-between",flexWrap:"wrap",gap:24}}>
                  <div style={{flex:1,minWidth:220}}>
                    <div className="fm" style={{fontSize:11,color:"var(--gold)",letterSpacing:"0.2em",marginBottom:14}}>ARCHITECTURAL ANALYSIS RESULT</div>
                    <h1 className="fd" style={{fontSize:"clamp(22px,4vw,38px)",marginBottom:14,lineHeight:1.2}}>{analysis.name}</h1>

                    {/* Location */}
                    <div style={{display:"flex",alignItems:"center",gap:5,marginBottom:14}}>
                      <I.Pin/><span style={{fontSize:15,color:"var(--ts)"}}>{analysis.location}</span>
                    </div>

                    {/* Badges */}
                    <div style={{display:"flex",gap:10,flexWrap:"wrap"}}>
                      <Badge>{analysis.style}</Badge>
                      <Badge color="teal">{analysis.architecture}</Badge>
                    </div>

                    {/* Meta grid */}
                    <div className="meta-row">
                      {analysis.built&&analysis.built!=="Ancient"&&<div className="meta-item"><span>Era / Built: </span>{analysis.built}</div>}
                      {analysis.builder&&<div className="meta-item"><span>Builder: </span>{analysis.builder}</div>}
                      {analysis.built&&<div className="meta-item"><span>Period: </span>{analysis.built}</div>}
                    </div>
                  </div>
                </div>

                {/* Description */}
                {analysis.description&&(
                  <div style={{marginTop:28,paddingTop:24,borderTop:"1px solid var(--bdr)"}}>
                    <p style={{fontSize:17,color:"var(--ts)",lineHeight:1.85}}>{analysis.description}</p>
                  </div>
                )}
              </div>

              {/* Features */}
              {analysis.features?.length>0&&(
                <div className="card" style={{padding:"28px 32px"}}>
                  <h3 className="fd" style={{fontSize:15,letterSpacing:"0.08em",marginBottom:20,color:"var(--ts)"}}>DETECTED ARCHITECTURAL FEATURES</h3>
                  <div style={{display:"flex",flexWrap:"wrap",gap:10}}>
                    {analysis.features.map(f=>(
                      <div key={f} style={{display:"flex",alignItems:"center",gap:8,background:"var(--bg-mid)",border:"1px solid var(--bdr)",borderRadius:6,padding:"8px 16px"}}>
                        <span className="gdot" style={{width:4,height:4}}/>
                        <span style={{fontSize:14,color:"var(--tp)"}}>{f}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* ── IMAGES TAB ── */}
          {tab==="images"&&(
            <div className="afi">
              <h2 className="fd" style={{fontSize:22,marginBottom:8}}>Monument Gallery</h2>
              <p style={{color:"var(--ts)",fontSize:15,marginBottom:28}}>Images sourced from Wikipedia for {analysis.name}.</p>

              {gallery.length>0?(
                <div style={{display:"grid",gridTemplateColumns:"repeat(auto-fill,minmax(260px,1fr))",gap:16}}>
                  {gallery.map((g,i)=>(
                    <div key={i} className="img-card" onClick={()=>setModal(g)}>
                      <img src={g.url} alt={g.caption}
                        onError={e=>{e.target.style.display="none";e.target.nextSibling.style.display="flex";}}
                      />
                      <div className="img-placeholder" style={{display:"none"}}><I.ImgErr/></div>
                      <div style={{padding:"10px 14px",background:"var(--bg-mid)",borderTop:"1px solid var(--bdr)"}}>
                        <div className="fm" style={{fontSize:11,color:"var(--tdim)",letterSpacing:"0.05em",overflow:"hidden",textOverflow:"ellipsis",whiteSpace:"nowrap"}}>{g.caption}</div>
                      </div>
                    </div>
                  ))}
                </div>
              ):(
                <div className="card" style={{padding:"60px 40px",textAlign:"center"}}>
                  <div style={{color:"var(--tdim)",marginBottom:12}}><I.Image/></div>
                  <div className="fd" style={{fontSize:16,marginBottom:8}}>No Images Available</div>
                  <p style={{color:"var(--ts)",fontSize:14}}>Wikipedia did not return images for this monument. Try visiting the Wikipedia page directly.</p>
                  <a href={`https://en.wikipedia.org/wiki/${analysis.name.replace(/ /g,"_")}`} target="_blank" rel="noreferrer" style={{display:"inline-flex",alignItems:"center",gap:6,marginTop:16,color:"var(--teal)",fontSize:14,textDecoration:"none"}}>View on Wikipedia <I.ExtLink/></a>
                </div>
              )}
            </div>
          )}

          {/* ── ANALYSIS TAB ── */}
          {tab==="analysis"&&(
            <div className="afi">
              <h2 className="fd" style={{fontSize:22,marginBottom:28}}>Architectural Style Analysis</h2>

              {/* Bar chart */}
              <div className="card" style={{padding:"32px",marginBottom:24}}>
                <h3 className="fd" style={{fontSize:15,letterSpacing:"0.08em",marginBottom:28,color:"var(--ts)"}}>STYLE PROBABILITY DISTRIBUTION</h3>
                <div style={{display:"flex",flexDirection:"column",gap:18}}>
                  {Object.entries(probs).sort((a,b)=>b[1]-a[1]).map(([style,pct],i)=>(
                    <div key={style}>
                      <div style={{display:"flex",justifyContent:"space-between",marginBottom:7}}>
                        <span className="fd" style={{fontSize:14}}>{style}</span>
                        <span className="fm" style={{fontSize:13,color:"var(--gold)"}}>{pct}%</span>
                      </div>
                      <div style={{height:8,background:"var(--bg-mid)",borderRadius:4,overflow:"hidden"}}>
                        <div style={{height:"100%",width:`${pct}%`,background:`linear-gradient(90deg,hsl(${40-i*6},55%,28%),hsl(${46-i*6},65%,48%))`,borderRadius:4,transition:"width 1s cubic-bezier(.4,0,.2,1)"}}/>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Stat cards */}
              <div style={{display:"grid",gridTemplateColumns:"repeat(auto-fit,minmax(160px,1fr))",gap:16}}>
                {[
                  {label:"Style",      value: analysis.style},
                  {label:"Architecture",value: analysis.architecture},
                  {label:"Era / Built", value: analysis.built||"—"},
                  {label:"Builder",    value: analysis.builder||"—"},
                  {label:"Location",   value: analysis.location},
                  {label:"Features",   value: analysis.features?.length||0},
                ].map(s=>(
                  <div key={s.label} className="card" style={{padding:"20px 18px",textAlign:"center"}}>
                    <div className="fd tgg" style={{fontSize:s.value?.toString().length>12?14:s.value?.toString().length>8?18:26,marginBottom:8,wordBreak:"break-word",lineHeight:1.2}}>{s.value}</div>
                    <div className="fm" style={{fontSize:10,color:"var(--tdim)",letterSpacing:"0.15em"}}>{s.label.toUpperCase()}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* ── SOURCES TAB ── */}
          {tab==="sources"&&(
            <div className="afi">
              <h2 className="fd" style={{fontSize:22,marginBottom:28}}>Research Sources</h2>
              <div style={{display:"flex",flexDirection:"column",gap:18}}>
                {(analysis.sources||[]).map((s,i)=>(
                  <div key={i} className="card cardg" style={{padding:"24px 28px",display:"flex",alignItems:"flex-start",gap:20}}>
                    <div style={{width:44,height:44,borderRadius:8,background:"var(--bg-mid)",border:"1px solid var(--bdr)",display:"flex",alignItems:"center",justifyContent:"center",flexShrink:0,color:"var(--gd)",fontSize:17,fontFamily:"'Cinzel',serif",fontWeight:700}}>{i+1}</div>
                    <div style={{flex:1}}>
                      <div style={{display:"flex",alignItems:"center",justifyContent:"space-between",marginBottom:8,flexWrap:"wrap",gap:8}}>
                        <h3 className="fd" style={{fontSize:16}}>{s.title}</h3>
                        <a href={s.url} target="_blank" rel="noreferrer" style={{display:"flex",alignItems:"center",gap:4,color:"var(--teal)",fontSize:12,fontFamily:"'JetBrains Mono',monospace",textDecoration:"none"}}>
                          {s.domain} <I.ExtLink/>
                        </a>
                      </div>
                      <p style={{fontSize:15,color:"var(--ts)",lineHeight:1.6}}>{s.description}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {modal&&<ImgModal url={modal.url} caption={modal.caption} onClose={()=>setModal(null)}/>}
    </div>
  );
}

// ─── ABOUT PAGE ───────────────────────────────────────────────────────────────
function AboutPage({ navigate, dark, toggle }) {
  return (
    <div style={{minHeight:"100vh"}}>
      <header style={{padding:"16px 40px",borderBottom:"1px solid var(--bdr)",display:"flex",alignItems:"center",justifyContent:"space-between",background:"var(--bg-mid)"}}>
        <Logo onClick={()=>navigate("landing")}/>
        <div style={{display:"flex",gap:10,alignItems:"center"}}><ThemeToggle dark={dark} toggle={toggle}/><button className="bng" style={{padding:"8px 20px",fontSize:13}} onClick={()=>navigate("login")}>Get Started</button></div>
      </header>
      <div style={{maxWidth:800,margin:"0 auto",padding:"80px 40px"}}>
        <div className="fm" style={{fontSize:11,color:"var(--gold)",letterSpacing:"0.2em",marginBottom:16}}>ABOUT</div>
        <h1 className="fd" style={{fontSize:"clamp(28px,5vw,52px)",marginBottom:32,lineHeight:1.2}}>Preserving Heritage<br/><span className="tgg">Through Intelligence</span></h1>
        <div style={{width:60,height:1,background:"var(--gd)",marginBottom:40}}/>
        <div style={{display:"flex",flexDirection:"column",gap:24,fontSize:18,color:"var(--ts)",lineHeight:1.85}}>
          <p>Vishwakarma AI uses CLIP (OpenAI's vision-language model) and FAISS vector search to identify monuments from a photograph, enriching results with Wikipedia descriptions and Ollama/Mistral LLM extraction.</p>
          <p>The platform recognises over 40 monuments across Dravidian, Chola, Hoysala, Vijayanagara, Nayaka, Mughal, Rajput, Buddhist, and other traditions.</p>
          <p>Our mission: make expert-level architectural identification accessible to researchers, heritage advocates, and curious minds.</p>
        </div>
        <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:24,marginTop:56}}>
          {[{n:"40+",l:"Monuments"},{n:"CLIP",l:"Vision Model"},{n:"Ollama",l:"LLM Engine"},{n:"FAISS",l:"Vector Search"}].map(s=>(
            <div key={s.l} className="card cardg" style={{padding:"28px",textAlign:"center"}}>
              <div className="fd tgg" style={{fontSize:38,marginBottom:8}}>{s.n}</div>
              <div style={{fontSize:15,color:"var(--ts)"}}>{s.l}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ─── CONTACT PAGE ─────────────────────────────────────────────────────────────
function ContactPage({ navigate, dark, toggle }) {
  const [sent, setSent] = useState(false);
  const [form, setForm] = useState({name:"",email:"",message:""});
  return (
    <div style={{minHeight:"100vh"}}>
      <header style={{padding:"16px 40px",borderBottom:"1px solid var(--bdr)",display:"flex",alignItems:"center",justifyContent:"space-between",background:"var(--bg-mid)"}}>
        <Logo onClick={()=>navigate("landing")}/>
        <div style={{display:"flex",gap:10,alignItems:"center"}}><ThemeToggle dark={dark} toggle={toggle}/><button className="bng" style={{padding:"8px 20px",fontSize:13}} onClick={()=>navigate("login")}>Get Started</button></div>
      </header>
      <div style={{maxWidth:640,margin:"0 auto",padding:"80px 40px"}}>
        <div className="fm" style={{fontSize:11,color:"var(--gold)",letterSpacing:"0.2em",marginBottom:16}}>CONTACT</div>
        <h1 className="fd" style={{fontSize:"clamp(28px,5vw,48px)",marginBottom:16}}>Get In Touch</h1>
        <p style={{fontSize:17,color:"var(--ts)",marginBottom:48,lineHeight:1.7}}>Questions, feedback, or collaboration proposals? We'd love to hear from you.</p>
        {sent?(
          <div className="card cardg afi" style={{padding:"40px",textAlign:"center"}}>
            <div style={{width:56,height:56,borderRadius:"50%",background:"rgba(201,168,76,.1)",border:"1px solid var(--gd)",display:"flex",alignItems:"center",justifyContent:"center",margin:"0 auto 20px",color:"var(--gold)"}}><I.Mail/></div>
            <h3 className="fd" style={{fontSize:22,marginBottom:12}}>Message Sent</h3>
            <p style={{color:"var(--ts)"}}>We'll respond within 2 business days.</p>
          </div>
        ):(
          <div className="card cardg" style={{padding:"40px"}}>
            <div style={{display:"flex",flexDirection:"column",gap:20}}>
              {[{k:"name",l:"NAME",t:"text",p:"Your name"},{k:"email",l:"EMAIL",t:"email",p:"you@example.com"}].map(f=>(
                <div key={f.k}><label style={{display:"block",fontSize:13,color:"var(--ts)",marginBottom:8,fontFamily:"'Cinzel',serif",letterSpacing:"0.1em"}}>{f.l}</label><input className="inp" type={f.t} placeholder={f.p} value={form[f.k]} onChange={e=>setForm({...form,[f.k]:e.target.value})}/></div>
              ))}
              <div><label style={{display:"block",fontSize:13,color:"var(--ts)",marginBottom:8,fontFamily:"'Cinzel',serif",letterSpacing:"0.1em"}}>MESSAGE</label><textarea className="inp" rows={5} style={{resize:"vertical"}} placeholder="Your message..." value={form.message} onChange={e=>setForm({...form,message:e.target.value})}/></div>
              <button className="bng" style={{padding:"14px",fontSize:14}} onClick={()=>setSent(true)}>Send Message</button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// ─── ROOT ─────────────────────────────────────────────────────────────────────
export default function App() {
  const { page, navigate } = useRouter();
  const { dark, toggle }   = useTheme();
  const [analysis, setAnalysis] = useState(null);
  const [history, setHistory]   = useState([]);

  // Load history from MongoDB on dashboard mount
  const loadHistory = useCallback(async () => {
    const token = localStorage.getItem("vk_token");
    if (!token) return;
    try {
      const items = await apiGetHistory(0, 20);
      setHistory(items);
    } catch(_) {}
  }, []);

  useEffect(() => {
    if (page === "dashboard" || page === "upload") loadHistory();
  }, [page, loadHistory]);

  const saveAnalysis = useCallback(d => {
    if (!d || d.error) return;
    const norm = { ...d, name: d.monument_name || d.name };
    setAnalysis(norm);
    // Prepend to local history list (full detail)
    setHistory(prev => [norm, ...prev.filter(h => (h.id||h._id) !== (norm.id||norm._id))].slice(0, 20));
  }, []);

  const handleLogout = useCallback(() => {
    localStorage.removeItem("vk_token");
    localStorage.removeItem("vk_user");
    setHistory([]);
    setAnalysis(null);
    navigate("landing");
  }, [navigate]);

  const sp = { dark, toggle };
  return (
    <>
      <style>{makeCSS(dark)}</style>
      {page==="landing"                       && <LandingPage  navigate={navigate} {...sp}/>}
      {page==="login"                         && <AuthPage mode="login"    navigate={navigate} {...sp}/>}
      {page==="register"                      && <AuthPage mode="register" navigate={navigate} {...sp}/>}
      {(page==="dashboard"||page==="upload")  && <Dashboard    navigate={navigate} history={history} setAnalysis={saveAnalysis} onLogout={handleLogout} {...sp}/>}
      {page==="analysis"                      && <AnalysisPage navigate={navigate} analysis={analysis} history={history} setAnalysis={saveAnalysis} onLogout={handleLogout} {...sp}/>}
      {page==="about"                         && <AboutPage    navigate={navigate} {...sp}/>}
      {page==="contact"                       && <ContactPage  navigate={navigate} {...sp}/>}
    </>
  );
}