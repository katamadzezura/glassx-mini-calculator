import json
import html
import uuid
from urllib.request import Request, urlopen
import streamlit as st

ROLL_WIDTH = 150.0
FILM_PRICE_USD = 150.0
INSTALL_PRICE_USD = 30.0

st.set_page_config(page_title='GlassX | Smart Film', page_icon='🟪', layout='centered', initial_sidebar_state='collapsed', menu_items={'Get Help':None,'Report a bug':None,'About':None})
st.markdown('''<style>
#MainMenu,footer,header[data-testid="stHeader"],[data-testid="stToolbar"],[data-testid="stDecoration"],[data-testid="stAppDeployButton"]{display:none!important}
.block-container{max-width:700px;padding-top:1.1rem;padding-bottom:3rem}
.brand{background:linear-gradient(110deg,#1c254e,#5140a3 70%,#8060c9);padding:24px 22px;border-radius:20px;color:#fff;margin-bottom:15px;box-shadow:0 8px 26px #332d7a25}
.brand strong{font-size:34px;letter-spacing:-1.2px}.brand p{font-size:13px;margin:4px 0 0;color:#ded8ff}
.stButton>button[kind="primary"],button[data-testid="stBaseButton-primary"]{background:linear-gradient(110deg,#5546bd,#8061db)!important;color:white!important;border:0!important}
.result{padding:22px;border-radius:18px;background:linear-gradient(120deg,#27265c,#5d49ac);color:white;margin:14px 0}
.result .value{font-size:clamp(29px,8vw,44px);font-weight:800;line-height:1.3}.result .minor{font-size:14px;color:#e5dfff}
.contact{border:1px solid #514b91;border-radius:18px;padding:20px;margin-top:18px;background:linear-gradient(145deg,#171b37,#282452);color:#fff}.contact h3{font-size:19px;margin:0 0 10px;color:#fff}.contact p{font-size:14px;line-height:1.7;color:#e1dff5}.call{display:block;text-align:center;text-decoration:none!important;background:#7763df;color:white!important;padding:13px;border-radius:12px;font-weight:750;margin-top:12px}.email{display:block;text-align:center;margin-top:13px;color:#ded8ff!important;text-decoration:underline!important;overflow-wrap:anywhere}
@media(max-width:600px){.block-container{padding-left:1rem;padding-right:1rem}}
</style>''',unsafe_allow_html=True)
T={
'ka':{'tag':'SMART FILM · სწრაფი ფასის გამოთვლა','intro':'შეიყვანეთ შუშების ზომები სანტიმეტრებში და მიიღეთ საორიენტაციო ფასი.','pane':'შუშა','w':'სიგანე (სმ)','h':'სიმაღლე (სმ)','qty':'რაოდენობა','add':'＋ შუშის დამატება','remove':'წაშლა','area':'საერთო ფართობი','price':'საორიენტაციო ღირებულება','note':'მითითებული ღირებულება საორიენტაციოა. ზუსტი ფასი განისაზღვრება ადგილზე აზომვისა და პროექტის ინდივიდუალური შეფასების შემდეგ.','invalid':'შეიყვანეთ ყველა შუშის სწორი, დადებითი ზომა.','rate':'ამჟამად ავტომატური კურსი მიუწვდომელია. ფასის გამოსათვლელად სცადეთ მოგვიანებით.','zero':'დაამატეთ შუშა დასათვლელად.','hint_w':'შეიყვანეთ სიგანე','hint_h':'შეიყვანეთ სიმაღლე','limit':'შუშის ორივე გვერდი 150 სმ-ზე მეტია; სტანდარტული ფირის რულონიდან ვერ დაიჭრება.'},
'en':{'tag':'SMART FILM · Instant estimate','intro':'Enter glass dimensions in centimeters to see an estimated price.','pane':'Panel','w':'Width (cm)','h':'Height (cm)','qty':'Quantity','add':'＋ Add panel','remove':'Delete','area':'Total area','price':'Estimated price','note':'This is an estimate. The exact price will be confirmed after an on-site measurement and individual project assessment.','invalid':'Enter valid positive dimensions for every panel.','rate':'Exchange rate is currently unavailable. Please try again later.','zero':'Add a panel to calculate.','hint_w':'Enter width','hint_h':'Enter height','limit':'Both dimensions exceed 150 cm; the panel cannot be cut from the standard film roll.'},
'ru':{'tag':'SMART FILM · Быстрый расчёт','intro':'Введите размеры стёкол в сантиметрах и получите примерную стоимость.','pane':'Стекло','w':'Ширина (см)','h':'Высота (см)','qty':'Количество','add':'＋ Добавить стекло','remove':'Удалить','area':'Общая площадь','price':'Примерная стоимость','note':'Указана ориентировочная стоимость. Точная цена определяется после замера на месте и индивидуальной оценки проекта.','invalid':'Укажите правильные положительные размеры каждого стекла.','rate':'Курс валют временно недоступен. Попробуйте позже.','zero':'Добавьте стекло для расчёта.','hint_w':'Введите ширину','hint_h':'Введите высоту','limit':'Обе стороны больше 150 см; стекло не помещается в стандартный рулон.'}}

lang=st.selectbox('Language / ენა / Язык',['ka','en','ru'],format_func=lambda k:{'ka':'🇬🇪 ქართული','en':'🇬🇧 English','ru':'🇷🇺 Русский'}[k],label_visibility='collapsed')
t=T[lang]
st.markdown(f'<div class="brand"><strong>GlassX</strong><p>{t["tag"]}</p></div>',unsafe_allow_html=True)
st.write(t['intro'])

def new_pane():
    return {'id':uuid.uuid4().hex}

if 'mini_panes' not in st.session_state:
    st.session_state.mini_panes=[new_pane()]

for i,p in enumerate(st.session_state.mini_panes):
    st.markdown(f'**{t["pane"]} {i+1}**')
    a,b=st.columns(2)
    p['w']=a.number_input(t['w'],min_value=0.0,value=None,step=1.0,placeholder=t['hint_w'],key=f'mini_w_{p["id"]}')
    p['h']=b.number_input(t['h'],min_value=0.0,value=None,step=1.0,placeholder=t['hint_h'],key=f'mini_h_{p["id"]}')
    c,d=st.columns([2,1])
    p['qty']=c.number_input(t['qty'],min_value=1,max_value=1000,value=1,step=1,key=f'mini_q_{p["id"]}')
    if d.button('🗑️ '+t['remove'],key=f'mini_del_{p["id"]}',disabled=len(st.session_state.mini_panes)==1,use_container_width=True):
        removed=p['id']
        st.session_state.mini_panes=[x for x in st.session_state.mini_panes if x['id']!=removed]
        for prefix in ('mini_w_', 'mini_h_', 'mini_q_'):
            st.session_state.pop(prefix+removed,None)
        st.rerun()
    st.divider()
if st.button(t['add'],use_container_width=True):
    st.session_state.mini_panes.append(new_pane())
    st.rerun()

@st.cache_data(ttl=3600,show_spinner=False)
def usd_gel():
    url='https://nbg.gov.ge/gw/api/ct/monetarypolicy/currencies/ka/json/?currencies=USD'
    req=Request(url,headers={'User-Agent':'GlassXMini/1.0','Accept':'application/json'})
    with urlopen(req,timeout=8) as r:
        data=json.load(r)
    cur=next(c for c in data[0]['currencies'] if c['code']=='USD')
    rate=float(cur['rate'])/float(cur.get('quantity',1))
    if not 0.1<rate<100:
        raise ValueError('Invalid exchange rate')
    return rate

# The same shelf-packing algorithm and sorting variants as the professional GlassX calculator.
# Like its default setting, panels are not rotated unless their width exceeds the roll width.
def pack(order):
    shelves=[]
    for piece in order:
        orientations=[(piece['width'],piece['height'])]
        if piece['width']>ROLL_WIDTH and piece['width']!=piece['height']:
            orientations.append((piece['height'],piece['width']))
        best=None
        for w,h in orientations:
            if w>ROLL_WIDTH+1e-8:
                continue
            for j,shelf in enumerate(shelves):
                if w<=ROLL_WIDTH-shelf['used']+1e-8 and h<=shelf['height']+1e-8:
                    score=(0,shelf['height']-h,ROLL_WIDTH-shelf['used']-w)
                    if best is None or score<best[0]:
                        best=(score,j,w,h)
            score=(1,h,ROLL_WIDTH-w)
            if best is None or score<best[0]:
                best=(score,None,w,h)
        if best is None:
            return None
        _,j,w,h=best
        if j is None:
            shelves.append({'used':w,'height':h})
        else:
            shelves[j]['used']+=w
    return sum(s['height'] for s in shelves)

panes=st.session_state.mini_panes
filled=bool(panes) and all(p.get('w') is not None and p.get('h') is not None and p['w']>0 and p['h']>0 for p in panes)
if filled:
    if any(min(p['w'],p['h'])>ROLL_WIDTH for p in panes):
        st.error(t['limit'])
    else:
        pieces=[{'width':float(p['w']),'height':float(p['h'])} for p in panes for _ in range(int(p['qty']))]
        orders=[
            sorted(pieces,key=lambda p:p['width']*p['height'],reverse=True),
            sorted(pieces,key=lambda p:max(p['width'],p['height']),reverse=True),
            sorted(pieces,key=lambda p:min(p['width'],p['height']),reverse=True),
            sorted(pieces,key=lambda p:p['height'],reverse=True),
        ]
        lengths=[length for order in orders if (length:=pack(order)) is not None]
        if not lengths:
            st.error(t['limit'])
        else:
            glass_area=sum(p['width']*p['height'] for p in pieces)/10000
            film_area=ROLL_WIDTH*min(lengths)/10000
            total_usd=film_area*FILM_PRICE_USD+glass_area*INSTALL_PRICE_USD
            try:
                rate=usd_gel()
                total_gel=total_usd*rate
                st.markdown(f'<div class="result"><div class="minor">{t["area"]}: {glass_area:,.2f} m²</div><div class="minor" style="margin-top:12px">{t["price"]}</div><div class="value">{total_gel:,.2f} ₾</div></div>',unsafe_allow_html=True)
                st.caption(t['note'])
            except Exception:
                st.warning(t['rate'])
elif panes and any(p.get('w') is not None or p.get('h') is not None for p in panes):
    st.info(t['invalid'])
else:
    st.caption(t['zero'])

contact={
    'ka':('დაგაინტერესათ Smart Film?','დამატებითი ინფორმაციისთვის მოგვწერეთ პირად შეტყობინებაში ან დაგვიკავშირდით ტელეფონით.','დარეკეთ: 599 263 263'),
    'en':('Interested in Smart Film?','For more information, send us a private message on Facebook or call us.','Call: 599 263 263'),
    'ru':('Заинтересовала Smart Film?','Для дополнительной информации напишите нам в личные сообщения Facebook или позвоните.','Позвонить: 599 263 263'),
}[lang]
st.markdown('<div class="contact"><h3>'+html.escape(contact[0])+'</h3><p>'+html.escape(contact[1])+'</p>'
            '<a class="call" href="tel:+995599263263">☎ '+html.escape(contact[2])+'</a>'
            '<a class="email" href="mailto:glassx.georgia@gmail.com">✉ glassx.georgia@gmail.com</a></div>',unsafe_allow_html=True)
