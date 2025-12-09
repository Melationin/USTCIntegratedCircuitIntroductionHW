import math

import streamlit as st
from matplotlib.pyplot import ylabel

from calc import getData,read_csv
import base64

st.set_page_config(
    page_title="CMOS反相器",
    layout="centered",  # 设置为"wide"或"centered"
    initial_sidebar_state="expanded"
)


def set_background_image(image_path):
    """设置背景图片"""
    css = f"""
    <style>
        [data-testid="stImage"] img {{
        border: 5px solid #DDDDDD;  /* 边框宽度 5px, 实线, 颜色为 Streamlit 的红色 */
        width: 100px;
        border-radius: 10px;      
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2); /
        }}
        [data-testid="stSidebar"] {{
            background-color: #dddddd;
            /* --- 边框设置 --- */
    border: 3px solid #dddddd;  /* 边框宽度 3px, 实线, 颜色为深灰色 */
    
    /* --- 圆角设置 --- */
    border-radius: 15px;        /* 设置 15 像素的圆角 */
    
    /* --- 增强立体感（可选）--- */
    box-shadow: 0px 5px 15px rgba(0, 0, 0, 0.2); /* 增加阴影，使其看起来更像一个浮动的卡片 */
    
    /* --- 调整内边距（可选）--- */
    /* padding: 20px; */
        }}       
        /* 调整文字颜色确保可读性 */
        .stMarkdown, .stTitle, .stHeader {{
            color: #333333;
        }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

@st.cache_resource
def draw(C,MaxTime,PMOSW,NMOSW):
    data = getData(C=C*1e-9,MaxTime=MaxTime*1e-3,PMOSW=PMOSW*1e-9,NMOSW=NMOSW*1e-9)
    T = data[0]
    Vin = data[1]
    Vout = data[2]
    #st.subheader("CMOS inverter")
    st.line_chart(data={"T(s)": T, "Vin(V)": Vin, "Vout(V)": Vout}, x="T(s)", y=("Vin(V)", "Vout(V)"),
                  x_label="T(s)", y_label="V(V)",
                  )

@st.cache_resource
def draw2():
    data = read_csv('C.csv')
    C = data[0]
    up_time = data[1]
    down_time = data[2]
    #st.subheader("CMOS inverter")
    st.line_chart(data={"C(nF)": C, "上升时间(us)": up_time, "下降时间(us)": down_time }, x="C(nF)", y=("上升时间(us)", "下降时间(us)"),
                  y_label="上升/下降时间(us)"
                  )
@st.cache_resource
def drawPMOSW():
    data = read_csv('PMOSW.csv')
    C = data[0]
    up_time = data[1]
    down_time = data[2]
    #st.subheader("CMOS inverter")
    st.line_chart(data={"PMOSW(nm)": C, "上升时间(us)": up_time, "下降时间(us)": down_time }, x="PMOSW(nm)", y=("上升时间(us)", "下降时间(us)"),
                  y_label="上升/下降时间(us)"
                  )

@st.cache_resource
def drawNMOSW():
    data = read_csv('NMOSW.csv')
    C = data[0]
    up_time = data[1]
    down_time = data[2]
    #st.subheader("CMOS inverter")
    st.line_chart(data={"NMOSW(nm)": C, "上升时间(us)": up_time, "下降时间(us)": down_time }, x="NMOSW(nm)", y=("上升时间(us)", "下降时间(us)"),
                  y_label="上升/下降时间(us)"
                  )

st.title("CMOS inverter数字逻辑功能分析 ")
set_background_image("bg.jpg")



# 在侧边栏创建控制部件
st.sidebar.header("控制参数")




min_val = 0.1
max_val = 1000
log_min = math.log10(min_val)
log_max = math.log10(max_val)
c = st.sidebar.slider("Cload(nF)", 0.05, 5.0,2.5,0.05,help="最终的Cload为两个滑动条数据之和")
c += st.sidebar.slider("Cload(nF)(大量程)", 0.0, 50.0,0.0,0.5,help="最终的Cload为两个滑动条数据之和")
time = st.sidebar.slider("模拟时长(ms)", 1.0, 10.0, 3.0, 0.1)
NMOSW = st.sidebar.slider("NMOS宽长(nm)", 1.0, 500.0, 250.0, 0.1)
PMOSW = st.sidebar.slider("PMOS宽长(nm)", 1.0, 500.0, 250.0, 0.1)




with st.container():

    st.markdown('''
    ## 实验目的：\n
-	搭建CMOS Inverter并验证器反向功能
-	使用脉冲信号输入，扫描$V_{in}→ V_{out}$
-	在反相器输出端添加负载电容$C_{load}$，调节电容大小，观察不同电容大小对输出跳变时间快慢的影响
-	修改MOSFET宽长，再次观察上升时间和下降时间的变化

    
    
    
    ''')
    st.header("1.搭建CMOS inverter 电路图")
    st.image("Draft7.png",caption="CMOS inverter 电路图")
    st.markdown('''
    &emsp;&emsp;上图是使用LTSPICE 搭建的电路图。 电路采用 $V_{DD} = 5\\text{V}$ 供电，作为逻辑高电平。输入端 $V_{in}$ 接入频率为 $1\\text{kHz}$ 的脉冲方波信号。上方 PMOS $M2$ 的源极接 $V_{CC}$，下方 NMOS $M1$ 的源极接地，两管的栅极相连作为输入 $V_{in}$ 。$M1$ 和 $M2$ 的漏极连接在一起，作为输出 $V_{out}$。输出端 $V_{out}$ 带有接地的电容负载 $C_L(图中为C1)$。
    ''',unsafe_allow_html=True)
    imageMode = st.toggle("信号输入模式",help="高电平/低电平")
    if imageMode:
        st.image("F2.png",caption="CMOS inverter 示意图(Vin为高电平)")
    else:
        st.image("F1.png",caption="CMOS inverter 示意图(Vin为低电平)")
    st.markdown('''
    &emsp;&emsp;当输入为低电平时, PMOS 导通、$V_{DD}$接通到输出$V_{out}$, 为高电平；输入为高电平时 NMOS 导通、$V_{SS}$接通到输出$V_{out}$,为低电平。
    ''')
    st.header("2.仿真与数据处理")
    st.markdown("&emsp;&emsp;由于原版LTSPICE的自动化功能相对偏弱，为了更好的分析和展示数据，使用PyLTSpice库，在python中导入LTSPICE生成的.net文件，进行批量仿真，同时利用python进行数据处理。")
    st.markdown('''
    &emsp;&emsp;在参数设置上，交互化展示的负载电容范围为0.05nF-55nF, PMOS和NMOS宽长(W)范围为1nm-500nm。PMOS和NMOS 其他参数在实验中保持不变，具体如下
    + $V_{th} = 0.0V$
    + $K_p$ =  $20 \\mu A/V^2$
    + $\\lambda$ = $0.0 V⁻¹$
    + $\\gamma$ = $0.0 V^{1/2}$
    + $R_D=R_S=0.0 \\Omega$
    + $C_{gd}=C_{gs} = 0.0 F/m$
    
    ''')
    st.markdown("&emsp;&emsp;基于Web，我们得到了可交互的$T - V_{in},V_{out}$曲线。同时，针对不同的C和不同的MOS宽长，通过对相邻数据点的线性插值，得到穿过高/低电平阈值(按照mos标准,高电平阈值为3.5V,低电平阈值为1.5V)的时间，以计算上升时间和下降时间,得到\"$C_{load}$-上升时间,下降时间\"曲线和\"MOS宽长-上升时间,下降时间\"曲线.(前者mos宽度统一为250nm, 后者负载电容为2.5nF)")
    st.header("3.数据分析")
    st.markdown(" &emsp;&emsp;借助于web技术，我们得到如下曲线。可以通过侧边栏的参数设置实时改变参数,观察曲线变化情况")
    #st.header("CMOS inverter 输入输出分析",help="可以通过侧边栏更改数据，以观察不同参数下输入输出的表现")
    draw(C=c,MaxTime=time,PMOSW=PMOSW,NMOSW=NMOSW)
    st.markdown("#### 3.1 负载电容($C_L$)的影响")
    st.markdown("&emsp;&emsp;通过数据处理，我们得到如下\"$C_{load}-上升/下降时间$\"曲线")
    draw2()
    st.markdown('''
    &emsp;&emsp;从实验数据可以看出：随着电容增大，上升/下降时间基本线性增长。在电容大于14nF时，下降时间和上升时间曲线出现噪声是由于LTSPICE模拟步长过大，但整体上仍符合线性关系。\n
    &emsp;&emsp;成线性这是因为RC电路充放电时间($\\tau$)与负载电阻($R_{eq}$)，电容($C_L$)成正比($\\tau \\propto R_{eq} C_L$)，随着电容增大而增大。\n
    &emsp;&emsp;在时间波形中：电容小时，输出边沿陡峭；电容大时，输出边沿变缓，甚至呈现“弧形指数充电/放电”
    ''')
    st.markdown("#### 3.2 MOS宽长的影响")
    st.markdown("通过数据处理，我们得到如下两组数据")
    drawPMOSW()
    drawNMOSW()
    st.markdown('''
    &emsp;&emsp;实验数据显示：增大 MOSFET 宽度，上升/下降时间明显变短。这是因为通道电阻降低。\n
    &emsp;&emsp;其中通道电阻满足
    $$
    R_{on} \\propto \\frac{L}{μ C_{ox}W(V_{GS}-V_{th})} 
    $$
    &emsp;&emsp;即通道电阻 与MOSFET宽度呈反比。结合RC电路充放电时间，可知理论分析符合实验数据。再由电容不变的情况下，上升/下降时间与电阻成正比，可知上升/下降时间与MOS宽度呈反比，符合实验数据。
    ''')

    st.markdown("&emsp;&emsp;同时，结合实验数据，可以得出上升时间只与PMOS宽长有关，下降时间也只与NMOS宽长有关，与电路分析吻合。")

    st.header("4. 结论")
    st.markdown('''
    &emsp;&emsp;本实验成功验证了CMOS Inverter的逻辑功能与延迟特性，直观展示了CMOS门速度由器件尺寸与电容共同决定。输出延迟和上升/下降时间随负载电容增大而显著变慢，符合RC模型。增大晶体管宽度能明显提升驱动能力、降低延迟，但会增加面积和功耗。
''')
