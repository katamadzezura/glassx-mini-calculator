import json
import uuid
from urllib.request import Request, urlopen
import streamlit as st

st.set_page_config(page_title='GlassX | Smart Film', page_icon='🟪', layout='centered', initial_sidebar_state='collapsed', menu_items={'Get Help':None,'Report a bug':None,'About':None})
st.markdown('''<style>
#MainMenu,footer,header[data-testid="stHeader"],[data-testid="stToolbar"],[data-testid="stDecoration"],[data-testid="stAppDeployButton"]{display:none!important}
.block-container{max-width:700px;padding-top:1.1rem;padding-bottom:3rem}
.brand{background:linear-gradient(110deg,#1c254e,#5140a3 70%,#8060c9);padding:24px 22px;border-radius:20px;color:#fff;margin-bottom:15px;box-shadow:0 8px 26px #332d7a25}
.brand strong{font-size:34px;letter-spacing:-1.2px}.brand p{font-size:13px;margin:4px 0 0;color:#ded8ff}
.stButton>button[kind="primary"],button[data-testid="stBaseButton-primary"]{background:linear-gradient(110deg,#5546bd,#8061db)!important;color:white!important;border:0!important}
.result{padding:22px;border-radius:18px;background:linear-gradient(120deg,#27265c,#5d49ac);color:white;margin:14px 0}
.result .value{font-size:clamp(29px,8vw,44px);font-weight:800;line-height:1.3}.result .minor{font-size:14px;color:#e5dfff}
@media(max-width:600px){.block-container{padding-left:1rem;padding-right:1rem}}
</style>''',unsafe_allow_html=True)
T={
'ka':{'tag':'SMART FILM · სწრაფი ფასის გამოთვლა','intro':'შეიყვანეთ შუშების ზომები სანტიმეტრებში და მიიღეთ საორიენტაციო ფასი.','pane':'შუშა','w':'სიგანე (სმ)','h':'სიმაღლე (სმ)','qty':'რაოდენობა','add':'＋ შუშის დამატება','remove':'წაშლა','area':'საერთო ფართობი','price':'საორიენტაციო ღირებულება','note':'საბოლოო ფასი დაზუსტდება ადგილზე აზომვის შემდეგ.','invalid':'შეიყვანეთ ყველა შუშის სწორი, დადებითი ზომა.','rate':'ამჟამად ავტომატური კურსი მიუწვდომელია. ფასის გამოსათვლელად სცადეთ მოგვიანებით.','zero':'დაამატეთ შუშა დასათვლელად.','limit':'შუშის ორივე გვერდი 150 სმ-ზე მეტია; სტანდარტული ფირის რულონიდან ვერ დაიჭრება.'},
'en':{'tag':'SMART FILM · Instant estimate','intro':'Enter glass dimensions in centimeters to see an estimated price.','pane':'Panel','w':'Width (cm)','h':'Height (cm)','qty':'Quantity','add':'＋ Add panel','remove':'Delete','area':'Total area','price':'Estimated price','note':'Final price is subject to on-site measurement.','invalid':'Enter valid positive dimensions for every panel.','rate':'Exchange rate is currently unavailable. Please try again later.','zero':'Add a panel to calculate.','limit':'Both dimensions exceed 150 cm; the panel cannot be cut from the standard film roll.'},
'ru':{'tag':'SMART FILM · Быстрый расчёт','intro':'Введите размеры стёкол в сантиметрах и получите примерную стоимость.','pane':'Стекло','w':'Ширина (см)','h':'Высота (см)','qty':'Количество','add':'＋ Добавить стекло','remove':'Удалить','area':'Общая площадь','price':'Примерная стоимость','note':'Окончательная цена уточняется после замера на месте.','invalid':'Укажите правильные положительные размеры каждого стекла.','rate':'Курс валют временно недоступен. Попробуйте позже.','zero':'Добавьте стекло для расчёта.','limit':'Обе стороны больше 150 см; стекло не помещается на стандартный рулон.'}}
lang=st.selectbox('Language / ენა / Язык',['ka','en','ru'],format_func=lambda k:{'ka':'🇬🇪 ქართული','en':'🇬🇧 English','ru':'🇷🇺 Русский'}[k],label_visibility='collapsed')
t=T[lang]
st.markdown(f'<div class="brand"><strong>GlassX</strong><p>{t["tag"]}</p></div>',unsafe_allow_html=True)
st.write(t['intro'])

def new_pane(): return {'id':uuid.uuid4().hex}
if 'mini_panes' not in st.session_state:st.session_state.mini_panes=[new_pane()]
for i,p in enumerate(st.session_state.mini_panes):
    st.markdown(f'**{t["pane"]} {i+1}**')
    a,b=st.columns(2)
    p['w']=a.number_input(t['w'],min_value=0.0,value=None,step=1.0,placeholder='100',key=f'mini_w_{p["id"]}')
    p['h']=b.number_input(t['h'],min_value=0.0,value=None,step=1.0,placeholder='180',key=f'mini_h_{p["id"]}')
    c,d=st.columns([2,1])
    p['qty']=c.number_input(t['qty'],min_value=1,max_value=1000,value=1,step=1,key=f'mini_q_{p["id"]}')
    if d.button('🗑️ '+t['remove'],key=f'mini_del_{p["id"]}',disabled=len(st.session_state.mini_panes)==1,use_container_width=True):
        st.session_state.mini_panes=[x for x in st.session_state.mini_panes if x['id']!=p['id']]
        st.rerun()
    st.divider()
if st.button(t['add'],use_container_width=True):
    st.session_state.mini_panes.append(new_pane())
    st.rerun()

@st.cache_data(ttl=3600,show_spinner=False)
def usd_gel():
    url='https://nbg.gov.ge/gw/api/ct/monetarypolicy/currencies/ka/json/?currencies=USD'
    req=Request(url,headers={'User-Agent':'GlassXMini/1.0','Accept':'application/json'})
    with urlopen(req,timeout=8) as r: data=json.load(r)
    cur=next(c for c in data[0]['currencies'] if c['code']=='USD')
    rate=float(cur['rate'])/float(cur.get('quantity',1))
    if not 0.1<rate<100:raise ValueError('Invalid exchange rate')
    return rate

panes=st.session_state.mini_panes
filled=all(p.get('w') is not None and p.get('h') is not None and p['w']>0 and p['h']>0 for p in panes)
if filled:
    if any(min(p['w'],p['h'])>150 for p in panes):
        st.error(t['limit'])
    else:
        area=sum(p['w']*p['h']*p['qty']/10000 for p in panes)
        try:
            rate=usd_gel()
            # Public customer price is configured in USD per square meter.
            total=area*180.0*rate
            st.markdown(f'<div class="result"><div class="minor">{t["area"]}: {area:,.2f} m²</div><div class="minor" style="margin-top:12px">{t["price"]}</div><div class="value">{total:,.2f} ₾</div></div>',unsafe_allow_html=True)
            st.caption(t['note'])
        except Exception:
            st.warning(t['rate'])
elif any(p.get('w') is not None or p.get('h') is not None for p in panes):
    st.info(t['invalid'])
else:
    st.caption(t['zero'])
