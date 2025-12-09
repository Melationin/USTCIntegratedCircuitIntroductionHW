# 这是USTC集成科技电路导论大作业！

本作业选择电路题目 1：CMOS 反相器（NOT Gate）的 数字逻辑功能分析。使用了python streamlit库构建了web界面，并通过pyltspice库实时调用ltspice进行仿真。

因此，在本地使用时，必须安装ltspice。

在windows系统下，先点击 安装运行库.bat ， 然后点击 启动网页.bat即可 


# 项目说明

Draft7.net 文件是ltspice电路仿真文件。可以通过pyltspice读取他进行仿真。

Draft7.png F1.png F2.png是图示所需。

C.csv PMOSW.csv NMOSW.csv则是提前计算好的数据。其数据生成可以通过calc.py 中最后一段

app.py 辅助主要的网页显示，calc.py则负责计算。
