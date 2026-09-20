"""Shared visual language and navigation for RoyReview."""

import html

import streamlit as st


def esc(value):
    return html.escape(str(value or ""))


def inject_design_system():
    st.markdown(
        """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@600;700;800&display=swap');
:root { --bg:#F4F4F4; --ink:#17181C; --dark:#393A3A; --muted:#575959; --blue:#B8D5E5; --primary:#F89344; --accent:#FF642F; --white:#FFFFFF; --line:#DDE0E0; --r-control:14px; --r-card:24px; }
.stApp { background:var(--bg); color:var(--ink); font-family:'DM Sans',sans-serif; }
#MainMenu, footer, [data-testid='stToolbar'] { display:none; } header[data-testid='stHeader'] { background:transparent; }
.block-container { max-width:1200px; padding:24px 32px 72px; }
h1,h2,h3,.rr-display { font-family:'Plus Jakarta Sans',sans-serif; color:var(--ink); letter-spacing:0; }
div[data-testid='stTextInput'] label, div[data-testid='stTextArea'] label, div[data-testid='stNumberInput'] label, div[data-testid='stSelectbox'] label { color:var(--muted)!important; font-size:.82rem!important; font-weight:700!important; }
div[data-baseweb='input'], div[data-baseweb='textarea'], div[data-baseweb='select'] > div { background:var(--white)!important; border-radius:var(--r-control)!important; border-color:var(--line)!important; }
div[data-baseweb='input']:focus-within, div[data-baseweb='textarea']:focus-within { border-color:var(--accent)!important; box-shadow:0 0 0 3px rgba(255,100,47,.14)!important; }
div[data-baseweb='input'] input, div[data-baseweb='textarea'] textarea { color:var(--ink)!important; }
div.stButton>button, div[data-testid='stFormSubmitButton']>button { min-height:42px; border-radius:var(--r-control); border:1px solid var(--line); background:var(--white); color:var(--ink); font-family:'DM Sans',sans-serif; font-weight:700; transition:transform .16s ease,background .16s ease,border-color .16s ease; }
div.stButton>button:hover, div[data-testid='stFormSubmitButton']>button:hover { transform:translateY(-1px); border-color:var(--accent); color:var(--ink); }
div.stButton>button:active, div[data-testid='stFormSubmitButton']>button:active { transform:translateY(0); }
div.stButton>button[kind='primary'], div[data-testid='stFormSubmitButton']>button[kind='primary'] { background:var(--accent); border-color:var(--accent); color:var(--white); }
div.stButton>button[kind='primary']:hover, div[data-testid='stFormSubmitButton']>button[kind='primary']:hover { background:var(--primary); border-color:var(--primary); color:var(--ink); }
.rr-nav { display:flex; align-items:center; justify-content:space-between; padding:10px 0 26px; }
.rr-brand { font:800 24px 'Plus Jakarta Sans',sans-serif; color:var(--dark); }.rr-brand span{color:var(--accent)}
.rr-nav-note,.rr-kicker { color:var(--muted); font-size:11px; font-weight:700; letter-spacing:1.2px; text-transform:uppercase; }
.rr-avatar { width:38px;height:38px;border-radius:50%;background:var(--dark);color:var(--white);display:grid;place-items:center;font-weight:800; }
.rr-hero { position:relative; overflow:hidden; padding:48px 52px; min-height:260px; border-radius:var(--r-card); background:var(--white); margin-bottom:32px; }.rr-hero:after{content:'';position:absolute;width:180px;height:180px;border-radius:50%;right:-45px;top:-55px;background:var(--blue);opacity:.55}.rr-hero>*{position:relative;z-index:1}.rr-hero h1{font-size:48px;line-height:1.06;margin:12px 0;max-width:680px}.rr-hero h1 span{color:var(--accent)}.rr-hero p{color:var(--muted);max-width:490px;line-height:1.6;margin:0}
.rr-section-head{display:flex;align-items:end;justify-content:space-between;margin:34px 0 14px}.rr-section-head h2{font-size:25px;margin:0}.rr-section-head p{margin:0;color:var(--muted);font-size:14px}
.st-key-verdict_segment { padding:4px; background:var(--white); border-radius:var(--r-control); margin:0 0 24px; }.st-key-verdict_segment div.stButton>button { border:0; background:transparent; }.st-key-verdict_segment .stButton:has(button[kind='primary']) button { background:var(--accent)!important;color:var(--white)!important; }
.rr-grid { margin-top:4px; }.rr-card { background:var(--white); border-radius:var(--r-control); overflow:hidden; margin-bottom:18px; transition:transform .18s ease, box-shadow .18s ease; }.rr-card:hover{transform:translateY(-3px);box-shadow:0 10px 25px rgba(57,58,58,.10)}.rr-poster{aspect-ratio:2/3;background:var(--blue);overflow:hidden}.rr-poster img{width:100%;height:100%;object-fit:cover;display:block}.rr-poster-empty{height:100%;display:grid;place-items:center;text-align:center;padding:16px;color:var(--dark);font-weight:700}.rr-card-copy{padding:14px}.rr-card-title{font:700 16px 'Plus Jakarta Sans',sans-serif;margin:9px 0 4px}.rr-card-meta{font-size:13px;color:var(--muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.rr-pill{display:inline-block;border-radius:999px;padding:5px 9px;background:#FFF0E6;color:var(--accent);font-size:10px;font-weight:800;text-transform:uppercase}.rr-rating{color:var(--accent);font-weight:800;font-size:13px;float:right}.rr-tag{display:inline-block;background:var(--blue);border-radius:999px;padding:4px 8px;margin-top:10px;font-size:11px;color:var(--dark)}
.rr-empty,.rr-panel,.rr-admin-card { border-radius:var(--r-card); background:var(--white); padding:28px; }.rr-empty{text-align:center;color:var(--muted);}.rr-empty strong{display:block;color:var(--ink);font:700 20px 'Plus Jakarta Sans',sans-serif;margin-bottom:7px}
.rr-details { background:var(--white);border-radius:var(--r-card);padding:32px;margin-top:16px }.rr-verdict{display:inline-block;color:var(--accent);font-size:12px;font-weight:800;text-transform:uppercase}.rr-movie-title{font:800 44px/1.08 'Plus Jakarta Sans',sans-serif;margin:10px 0}.rr-rating-block{background:var(--dark);color:var(--white);border-radius:var(--r-control);padding:18px 20px;margin:22px 0}.rr-rating-stars{color:var(--primary);font-size:27px;letter-spacing:2px}.rr-stats{display:flex;flex-wrap:wrap;gap:22px;margin:18px 0}.rr-stat label{display:block;color:var(--muted);font-size:10px;font-weight:800;letter-spacing:1px}.rr-stat b{font-size:14px}.rr-quote{border-left:4px solid var(--primary);margin:28px 0;padding:4px 0 4px 20px;color:var(--muted);font-size:17px;line-height:1.75}.rr-quote:before{content:'“';color:var(--accent);font:800 48px/0 'Plus Jakarta Sans',sans-serif;vertical-align:-14px;margin-right:7px}
.rr-ask{background:var(--blue);border-radius:var(--r-card);padding:28px;margin-top:28px}.rr-ask h2{font-size:26px;margin:8px 0}.rr-ask p{color:var(--dark);margin:0 0 18px}.rr-answer{background:var(--white);border-radius:var(--r-control);padding:20px;margin-top:18px}.rr-answer-q{font-size:12px;color:var(--muted);margin-bottom:10px}.rr-source{color:var(--muted);font-size:12px;margin-top:8px}
.rr-auth-shell{max-width:920px;margin:72px auto}.rr-auth-shell-single{max-width:420px}.rr-auth-card{background:var(--white);border-radius:var(--r-card);padding:34px;box-shadow:0 14px 36px rgba(57,58,58,.08)}.rr-auth-card h1{font-size:30px;margin:16px 0 6px}.rr-auth-card p{color:var(--muted);margin:0 0 22px}.rr-auth-tabs{background:var(--bg);padding:4px;border-radius:var(--r-control);margin-bottom:22px}.rr-auth-tabs div.stButton>button{border:0;background:transparent}.rr-auth-tabs .stButton:has(button[kind='primary']) button{background:var(--white)!important;color:var(--ink)!important;box-shadow:0 2px 8px rgba(57,58,58,.07)}
div[data-testid='stHorizontalBlock']:has(.rr-auth-brand){align-items:center}
.rr-stat-card{background:var(--white);border-radius:var(--r-control);padding:18px}.rr-stat-card label{display:block;color:var(--muted);font-size:11px;font-weight:800;text-transform:uppercase;letter-spacing:1px}.rr-stat-card strong{font:800 30px 'Plus Jakarta Sans',sans-serif}.rr-profile-avatar{width:88px;height:88px;border-radius:50%;object-fit:cover;background:var(--blue);display:grid;place-items:center;font:800 32px 'Plus Jakarta Sans',sans-serif}
.rr-footer{margin:48px 0 0;padding:28px 0 8px;border-top:1px solid var(--line);text-align:center}.rr-footer .rr-brand{font-size:16px;display:inline-block;margin-bottom:6px}.rr-footer-tagline{color:var(--muted);font-size:13px;margin:0 0 10px;line-height:1.5}.rr-footer-copy{color:var(--muted);font-size:12px;margin:0;opacity:.85}
.rr-auth-tabs {
    background: transparent !important;
    box-shadow: none !important;
    border: none !important;
    padding: 0 !important;
    margin: 0 !important;
}
@media(max-width:700px){.block-container{padding:18px 16px 52px}.rr-nav-note{display:none}.rr-hero{padding:34px 26px;min-height:0}.rr-hero h1{font-size:34px}.rr-details{padding:20px}.rr-movie-title{font-size:34px}.rr-section-head{align-items:start;gap:8px;flex-direction:column}.st-key-verdict_segment .stButton{min-width:125px}.rr-auth-shell{max-width:420px;margin:30px auto}.rr-auth-card{padding:24px}div[data-testid='stHorizontalBlock']:has(.rr-auth-brand){flex-direction:column!important;gap:18px}div[data-testid='stHorizontalBlock']:has(.rr-auth-brand)>div{width:100%!important;flex:1 1 100%!important}.rr-footer{margin-top:36px;padding-top:22px}}

</style>
        """,
        unsafe_allow_html=True,
    )


def render_nav(user):
    name = (user or {}).get("name") or (user or {}).get("username") or "R"
    initial = esc(name[:1].upper())
    left, _, avatar = st.columns([.58, .28, .14], vertical_alignment="center")
    with left:
        st.markdown('<div class="rr-brand">Cine<span>AI</span></div>', unsafe_allow_html=True)
    with _:
        st.markdown('<div class="rr-nav-note">Our personal movie journal</div>', unsafe_allow_html=True)
    with avatar:
        with st.popover("Profile", use_container_width=True):
            st.markdown(f'<div class="rr-avatar">{initial}</div>', unsafe_allow_html=True)
            if st.button("Profile", key="nav_profile", use_container_width=True):
                st.session_state["view"] = "profile"; st.rerun()
            if st.button("Edit profile", key="nav_edit_profile", use_container_width=True):
                st.session_state["view"] = "edit_profile"; st.rerun()
            if st.button("Sign out", key="nav_logout", use_container_width=True):
                st.session_state["logout_requested"] = True; st.rerun()


def render_footer():
    st.markdown(
        '<div class="rr-footer">'
        '<div class="rr-brand">Cine<span>AI</span></div>'
        '<p class="rr-footer-tagline">Movies, from Our\'s perspective.</p>'
        '<p class="rr-footer-copy">&copy; 2026 CineAI. All rights reserved.</p>'
        "</div>",
        unsafe_allow_html=True,
    )
