%===================================================

%===================================================


%导入需要的宏包
\RequirePackage{amsmath,amsthm,amsfonts,amssymb,bm,mathrsfs,upgreek,array, mathrsfs, times,indentfirst,multirow}
\RequirePackage{fancyhdr}

%依赖的Latex版本
\NeedsTeXFormat{LaTeX2e}[2005/12/01]
%声明本文档为模板类
\ProvidesClass{DLUT-thesis}

%根据用户选项LoadClass
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{ctexbook}}
\newif\if@isEnMaster\@isEnMasterfalse
\newif\if@isBachelor\@isBachelorfalse
\newif\if@isDoctor\@isDoctorfalse
\newif\if@isTwoSide\@isTwoSidefalse
%本科
\DeclareOption{Bachelor}{\@isBachelortrue}
%专硕
\DeclareOption{EnMaster}{\@isEnMastertrue}
%博士
\DeclareOption{Doctor}{\@isDoctortrue}
\DeclareOption{twoside}{\@isTwoSidetrue}
\ProcessOptions\relax

\LoadClass[zihao=-4,a4paper,oneside,openright,UTF8,space=auto]{ctexbook}

%\if@isTwoSide
%\LoadClass[zihao=-4,a4paper,twoside,openright,UTF8,space=auto]{ctexbook}
%\else
%\LoadClass[zihao=-4,a4paper,oneside,openright,UTF8,space=auto]{ctexbook}
%\fi


%定义使用者需要填写的标签
\def\DLUT@label@schoolNumber{学校代码:~}
\def\DLUT@label@classification{密级:~}
\def\DLUT@label@author{作者姓名:~}
\def\DLUT@label@studentNumber{学~~~~~~号:~}
\def\DLUT@label@advisor{导师姓名:~}
\def\DLUT@label@advisorTitle{职~~~~~~称:~}
\def\DLUT@label@engineeringMasterField{工程硕士专业领域:~}
\def\DLUT@label@degreeLevel{学位级别:~}
\def\DLUT@label@degreeType{学位类别:~}
\def\DLUT@label@major{学科专业:~}
\def\DLUT@label@researchArea{研究方向:~}

\def\DLUT@label@institute{学~~~~~~~~~~~院~~:~}
\def\DLUT@label@dutmajor{专~~~~~~~~~~~业~~:~}
\def\DLUT@label@author{学~生~姓~名~~:~}
\def\DLUT@label@studentNumber{学~~~~~~~~~~~号~~:~}
\def\DLUT@label@advisor{指~导~教~师~~:~}
\def\DLUT@label@reviewer{评~阅~教~师~~:~}
\def\DLUT@label@date{完~成~日~期~~:~}

% \def\DLUT@label@institute{Department:}
% \def\DLUT@label@dutmajor{Major:}
% \def\DLUT@label@author{Name:}
% \def\DLUT@label@studentNumber{Student Number:}
% \def\DLUT@label@advisor{Supervisor:}
% \def\DLUT@label@reviewer{Review Teacher:}
% \def\DLUT@label@date{Completion Date:}

%定义上述标签的默认值
\def\DLUT@value@schoolNumber{10004}
\def\DLUT@value@classification{公开}
\def\DLUT@value@author{XXXX}
\def\DLUT@value@studentNumber{XXXX}
\def\DLUT@value@advisor{XXXX}
\def\DLUT@value@advisorTitle{XXXX}
\def\DLUT@value@engineeringMasterField{XXXX}
\if@isDoctor
\def\DLUT@value@degreeLevel{博士}
\else
\def\DLUT@value@degreeLevel{硕士}
\fi
\def\DLUT@value@degreeType{XXXX}
\def\DLUT@value@major{XXXX}
\def\DLUT@value@researchArea{XXXX}
\def\DLUT@value@title{中文题目}
\def\DLUT@value@englishtitle{英文题目}
\def\DLUT@value@japanesetitle{日本题目}

\def\DLUT@value@institute{学~院（系）:~}
\def\DLUT@value@dutmajor{专业:~}
\def\DLUT@value@author{学~生~姓~名:~}
\def\DLUT@value@reviewer{评~阅~教~师:~}


%定义用户填写上述标签对应值的命令,需要用户在主文档自行调用
\newcommand\schooNumber[1]{\def\DLUT@value@schoolNumber{#1}}
\newcommand\classification[1]{\def\DLUT@value@classification{#1}}
\renewcommand\author[1]{\def\DLUT@value@author{#1}}
\newcommand\studentNumber[1]{\def\DLUT@value@studentNumber{#1}}
\newcommand\advisor[1]{\def\DLUT@value@advisor{#1}}
\newcommand\advisorTitle[1]{\def\DLUT@value@advisorTitle{#1}}
\newcommand\engineeringMasterField[1]{\def\DLUT@value@engineeringMasterField{#1}}
\newcommand\degreeType[1]{\def\DLUT@value@degreeType{#1}}
\newcommand\major[1]{\def\DLUT@value@major{#1}}
\newcommand\researchArea[1]{\def\DLUT@value@researchArea{#1}}
\newcommand\datetime[1]{\def\DLUT@label@datetime{#1}}
\renewcommand\title[1]{\def\DLUT@value@title{#1}}
\newcommand\chinesetitle[1]{\def\DLUT@value@chinesetitle{#1}}
\newcommand\englishtitle[1]{\def\DLUT@value@englishtitle{#1}}
\newcommand\japanesetitle[1]{\def\DLUT@value@japanesetitle{#1}}

\newcommand\institute[1]{\def\DLUT@value@institute{#1}}
\newcommand\dutmajor[1]{\def\DLUT@value@dutmajor{#1}}
\newcommand\reviewer[1]{\def\DLUT@value@reviewer{#1}}

%DLUT本科毕业设计论文封面
%制作内封
\newcommand{\makeDUTCover}{
	\newpage
	\pagenumbering{Roman}
	\thispagestyle{empty}
	%这里控制上下间距
	\vspace{3pt}
	\begin{center}
		~\par
		%~\par
		{\bfseries \songti\zihao{-1}\ziju{0}\DLUT@value@title\\}
		% {\bfseries \songti\zihao{-1}\ziju{0}{Dalian University of Technology Undergraduate Diploma Thesis (Design)}\\}
		%这里控制上下间距
		\vspace{50pt}
		{ \heiti\zihao{2}\ziju{0} \DLUT@value@chinesetitle\\}
		%这里控制上下间距
		\vspace{15pt}
		{\bfseries \zihao{3}\ziju{0}\DLUT@value@englishtitle\\}
	\end{center}
	%这里控制上下间距
	\vspace{110pt}

	\renewcommand\arraystretch{1.2}

	{\hspace{0pt}\songti\zihao{-3}\ziju{0}
		\begin{tabular}{lp{0mm}l}
			\DLUT@label@institute &\underline {\zihao{-4}~\DLUT@value@institute ~}\\
			\DLUT@label@dutmajor &\underline {~\DLUT@value@dutmajor ~}\\
			\DLUT@label@author &\underline {~\DLUT@value@author ~}\\
			\DLUT@label@studentNumber &\underline {~\DLUT@value@studentNumber ~}\\
			\DLUT@label@advisor &\underline {~\DLUT@value@advisor ~}\\
			\DLUT@label@reviewer &\underline {~\DLUT@value@reviewer ~}\\
			\DLUT@label@date &\underline {~\DLUT@label@datetime ~}\\
		\end{tabular}
	}
	\vfill
	\begin{center}
		\begin{figure}[h]
			\centering
			\includegraphics[width=0.32\textwidth]{dlut-logo.pdf}\\
			{\zihao{-4}Dalian University of Technology}
		\end{figure}

        
	\end{center}
}

%\pagestyle{fancy}

%版权授权书
\newcommand{\makeAuthorization}{
	\fancyhead{}
	\vspace{44pt}
	\chapter*{\centerline{\heiti\zihao{2} 原创性声明}}
	\thispagestyle{DLUT@headingNoNum}
          \vspace{20pt}
	\songti\zihao{-3}
	本人郑重声明：本人所呈交的毕业设计（论文），是在指导老师的指导下独立进行研究所取得的成果。毕业设计（论文）中凡引用他人已经发表或未发表的成果、数据、观点等，均已明确注明出处。除文中已经注明引用的内容外，不包含任何其他个人或集体已经发表或撰写过的科研成果。对本文的研究成果做出重要贡献的个人和集体，均已在文中以明确方式标明。\par
	~\par

	\noindent 本声明的法律责任由本人承担。
	
	\vspace{44pt}
	\noindent 作者签名：~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~日~~~~期：

	\newpage

	\vspace{44pt}
	\chapter*{\centerline{\heiti\zihao{2} 关于使用授权的声明}}
	\thispagestyle{DLUT@headingNoNum}
          \vspace{20pt}
	\songti\zihao{-3}
	本人在指导老师指导下所完成的毕业设计（论文）及相关的资料（包括图纸、试验记录、原始数据、实物照片、图片、录音带、设计手稿等），知识产权归属大连理工大学。本人完全了解大连理工大学有关保存、使用毕业设计（论文）的规定，本人授权大连理工大学可以将本毕业设计（论文）的全部或部分内容编入有关数据库进行检索，可以采用任何复制手段保存和汇编本毕业设计（论文）。如果发表相关成果，一定征得指导教师同意，且第一署名单位为大连理工大学。本人离校后使用毕业毕业设计（论文）或与该论文直接相关的学术论文或成果时，第一署名单位仍然为大连理工大学。\par
	~\par
	
	\vspace{44pt}
	\noindent 论文作者签名：~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~日~~~~期：\\
	\noindent 指导老师签名：~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~日~~~~期：
}

%重新定义致谢环境
\renewenvironment{thanks}{
	\zihao{-4}
	\chapter*{\centerline{\textbf{Acknowledgement}}}
	\markboth{Acknowledgement}{Acknowledgement}
	\addcontentsline{toc}{chapter}{Acknowledgement}
}{}

%定义中文摘要环境
\newenvironment{abstract}{
	\setcounter{page}{1}
	\zihao{-4}
	\chapter*{\centerline{摘~~~~要}}
	\markboth{摘要}{摘要}
	\addcontentsline{toc}{chapter}{摘要}
}{}

%定义英文摘要环境
\newenvironment{englishabstract}{
	\zihao{-4}
	{\centering \chapter*{\textbf{ \DLUT@value@englishtitle}}}
	\markboth{Abstract}{Abstract}
	\addcontentsline{toc}{chapter}{Abstract}
}{}

% %定义日文摘要环境
% \newenvironment{japaneseabstract}{
% 	\zihao{-4}
% 	\chapter*{\centerline{\textbf{\DLUT@value@japanesetitle}}}
% 	\markboth{摘要（日语）}{摘要（日语）}
% 	\addcontentsline{toc}{chapter}{摘要（日语）}
% }{}

%定义中英文关键词命令
\newcommand{\keywords}[1]{\textbf{\heiti 关键词：}#1}
\newcommand{\englishkeywords}[1]{\textbf{Key Words:~}#1}
\newcommand{\japanesekeywords}[1]{\textbf{キーワード:~}#1}



\newenvironment{preface}{
	\zihao{-4}
	\chapter*{\centerline{引~~~~言}}
	\markboth{引言}{引言}
	\addcontentsline{toc}{chapter}{引言}
}{}

\newenvironment{conclusion}{
	\zihao{-4}
	\chapter*{\centerline{\textbf{Conclusion}}}
	\markboth{Conclusion}{Conclusion}
	\addcontentsline{toc}{chapter}{Conclusion}
}{}

\newenvironment{modify}{
	\zihao{-4}
	\chapter*{\centerline{修改记录}}
	\markboth{修改记录}{修改记录}
	\addcontentsline{toc}{chapter}{修改记录}
}{}


\newenvironment{appendices}{
	\zihao{-4}
	\chapter*{\centerline{Appendices}}
	\markboth{Appendices}{Appendices}
	\addcontentsline{toc}{chapter}{Appendices}
}{}


%%定义正文的页眉页脚格式
\def\DLUT@chapter{}
\fancypagestyle{DLUT@heading}{
	\fancyhf{}
	\setlength{\headsep}{0.5cm}
	\setlength{\headheight}{26mm}
  	%\setlength{\footskip}{0.8cm}
  	\fancyhead[C]{
		\songti\zihao{5}\ziju{0}{\DLUT@value@englishtitle}
	}
  	\setlength{\footskip}{0.8cm}
	\fancyfoot[C]{\zihao{-5} -- ~ \thepage ~ --}
}

\fancypagestyle{DLUT@headingNoNum}{
	\fancyhf{}
	\setlength{\headsep}{0.5cm}
	\setlength{\headheight}{26mm}
  	%\setlength{\footskip}{0.8cm}
  	\fancyhead[C]{
		\songti\zihao{5}\ziju{0}{\DLUT@value@englishtitle}
	}
  	\setlength{\footskip}{0.8cm}
}



%\setlength{\headsep}{5cm}
%\setlength{\footskip}{10mm}


%%设置页边距和装订线
\usepackage[
top=2.9cm,
bottom=2.5cm,
left=2.1cm,
right=2.1cm,
bindingoffset=1cm,
%headheight=15pt
headheight=1.8cm
]{geometry}

%% 设置章节格式
\ctexset{chapter={
		name={},
		number = {\arabic{chapter}},
		format = { \heiti \zihao{-3}},
		pagestyle = {DLUT@heading},
		beforeskip = 26bp,
		afterskip = 24bp,
%       beforeskip = 24bp,
%		afterskip = 18bp,
		fixskip = true,
	}
}

%% 设置一级章节格式
\ctexset{section={
		format={\raggedright \heiti  \zihao{-3}},
		beforeskip = 28bp plus 1ex minus .2ex,
		afterskip = 24bp plus .2ex,
%                     beforeskip = 24bp,
%		afterskip = 18bp,
		fixskip = true,
	}
}

% 设置二级标题格式

%黑体小四加粗顶左，单倍行距，序号与题目间空一个汉字符

\ctexset{subsection={
		format = { \heiti \raggedright \zihao{4}},
		beforeskip =28bp plus 1ex minus .2ex,
		afterskip = 24bp plus .2ex,
%                     beforeskip = 24bp,
%		afterskip = 18bp,
		fixskip = true,
	}
}

% 设置三节标题格式：黑体小四居左书写，单倍行距，序号与题目间空一个汉字符

\ctexset{subsubsection={
		format={\heiti \raggedright \zihao{-4}},
		beforeskip=28bp plus 1ex minus .2ex,
		afterskip=24bp plus .2ex,
		fixskip=true,
	}
}


%目录
\ifxetex  % xelatex
\RequirePackage[xetex]{hyperref}
\hypersetup{
	bookmarksnumbered,
	colorlinks=true,
	linkcolor=black,
	citecolor=black,
	plainpages=false,
	pdfstartview=FitH
}
\else
\ifpdf
\RequirePackage[pdftex,unicode]{hyperref}
\hypersetup{
	bookmarksnumbered,
	colorlinks=true,
	linkcolor=black,
	citecolor=black,
	plainpages=false,
	pdfstartview=FitH
}
\else
\RequirePackage[dvipdfmx,unicode]{hyperref}
\hypersetup{
	bookmarksnumbered,
	colorlinks=true,
	linkcolor=black,
	citecolor=black,
	plainpages=false,
	pdfstartview=FitH
}
\fi
\fi

\addtocontents{toc}{\protect\hypersetup{hidelinks}}
\addtocontents{lot}{\protect\hypersetup{hidelinks}}
\addtocontents{lof}{\protect\hypersetup{hidelinks}}

\RequirePackage{titletoc}
\titlecontents{chapter}[0pt]{\songti \zihao{-4}}
{\thecontentslabel\hspace{\ccwd}}{}
{\hspace{.5em}\vspace{2.7bp}\titlerule*{.}\contentspage}

\titlecontents{section}[2\ccwd]{\songti \zihao{-4}}
{\thecontentslabel\hspace{\ccwd}}{}
{\hspace{.5em}\vspace{2.7bp}\titlerule*{.}\contentspage}

\titlecontents{subsection}[4\ccwd]{\songti \zihao{-4}}
{\thecontentslabel\hspace{\ccwd}}{}
{\hspace{.5em}\vspace{2.7bp}\titlerule*{.}\contentspage}

\titlecontents{figure}[0pt]{\songti\zihao{-4}}
{\figurename~\thecontentslabel\quad}{\hspace*{-1.5cm}}
{\hspace{.5em}\vspace{2.7bp}\titlerule*{.}\contentspage}

\titlecontents{table}[0pt]{\songti\zihao{-4}}
{\tablename~\thecontentslabel\quad}{\hspace*{-1.5cm}}
{\hspace{.5em}\vspace{2.7bp}\titlerule*{.}\contentspage}

\renewcommand\tableofcontents{%
	\chapter*{\heiti\zihao{-3}\centerline{\textbf{目录}}}%目录里显示“目录”，否则\chapter*
	\@mkboth{\MakeUppercase\contentsname}{\MakeUppercase\contentsname}%
	% \pdfbookmark[0]{目录}{bittoc}
	\@starttoc{toc}%
}


%设定文档页眉页脚
\pagestyle{DLUT@heading}
%必须在设置完文档的页眉页脚格式之后再重定义此命令
\renewcommand{\chaptermark}[1]{
	\markboth{#1}{}
}


%%定义制作论文封面命令
\newcommand{\makecover}{

}


%% graphics packages
\RequirePackage{graphicx}
%% 并列子图
\RequirePackage{subfigure}

\RequirePackage{wrapfig}
%%===========================设置图表标题选项==========================
\RequirePackage{amsmath}
\RequirePackage{caption}
\DeclareCaptionLabelSeparator{zhspace}{\hspace{1\ccwd}}
\DeclareCaptionFont{fontsize}{\zihao{5}}
\captionsetup{
	font = {fontsize},
	labelsep = zhspace,
}
\captionsetup[table]{
	position = top,
	aboveskip = 6bp,
	belowskip = 6bp,
}
\numberwithin{table}{chapter}
\captionsetup[figure]{
	position = bottom,
	aboveskip = 6bp,
	belowskip = 6bp,
}

%% 如果插入的图片没有指定扩展名，那么依次搜索下面的扩展名所对应的文件
\DeclareGraphicsExtensions{.pdf,.eps,.png,.jpg,.jpeg}
% ccaption -- bicaption
%\RequirePackage{ccaption}
%\captiondelim{\ }
%\captionnamefont{\songti\zihao{5}}
%\captiontitlefont{\songti\zihao{5}}


%% sort and compress citations
\RequirePackage[numbers,square,comma,super,sort&compress]{natbib}
% 上标引用
\newcommand{\upcite}[1]{\textsuperscript{\cite{#1}}}


% 将浮动参数设为较宽松的值
\renewcommand{\textfraction}{0.15}
\renewcommand{\topfraction}{0.85}
\renewcommand{\bottomfraction}{0.65}
\renewcommand{\floatpagefraction}{0.60}


% 定公式、图、表编号为"3-1"的形式，即分隔符由.变为短杠
\renewcommand\theequation{\arabic{chapter}.\arabic{equation}}
\renewcommand\thefigure{\arabic{chapter}.\arabic{figure}}
\renewcommand\thetable{\arabic{chapter}.\arabic{table}}

% 颜色宏包
\RequirePackage{xcolor}


% 中文破折号
\newcommand{\cndash}{\rule{0.0em}{0pt}\rule[0.35em]{1.4em}{0.05em}\rule{0.2em}{0pt}}

% listings 源代码显示宏包
\RequirePackage{listings}
\lstset{tabsize=4, %
	frame=shadowbox, %把代码用带有阴影的框圈起来
	commentstyle=\color{red!50!green!50!blue!50},%浅灰色的注释
	rulesepcolor=\color{red!20!green!20!blue!20},%代码块边框为淡青色
	keywordstyle=\color{blue!90}\bfseries, %代码关键字的颜色为蓝色，粗体
	showstringspaces=false,%不显示代码字符串中间的空格标记
	stringstyle=\ttfamily, % 代码字符串的特殊格式
	keepspaces=true, %
	breakindent=22pt, %
	numbers=left,%左侧显示行号
	stepnumber=1,%
	numberstyle=\tiny, %行号字体用小号
	basicstyle=\footnotesize, %
	showspaces=false, %
	flexiblecolumns=true, %
	breaklines=true, %对过长的代码自动换行
	breakautoindent=true,%
	breakindent=4em, %
	aboveskip=1em, %代码块边框
	%% added by http://bbs.ctex.org/viewthread.php?tid=53451
	fontadjust,
	captionpos=t,
	framextopmargin=2pt,framexbottommargin=2pt,abovecaptionskip=-3pt,belowcaptionskip=3pt,
	xleftmargin=4em,xrightmargin=4em, % 设定listing左右的空白
	texcl=true,
	% 设定中文冲突，断行，列模式，数学环境输入，listing数字的样式
	extendedchars=false,columns=flexible,mathescape=true
	numbersep=-1em
}
\renewcommand{\lstlistingname}{代码} %% 重命名Listings标题头

%% enumerate 列表环境间距调节
\usepackage{enumitem}
% \setenumerate[1]{itemsep=0pt,partopsep=0pt,parsep=\parskip,topsep=5pt}
% \setitemize[1]{itemsep=0pt,partopsep=0pt,parsep=\parskip,topsep=0pt}
% \setdescription{itemsep=0pt,partopsep=0pt,parsep=\parskip,topsep=5pt}

%_  参考文献风格 added by wei.jianwen@gmail.com
\bibliographystyle{GBT7714-2005NLang}

%_ 参考文献环境
\renewenvironment{thebibliography}[1]
{\zihao{5}
	\chapter*{\centerline{\textbf{References}}}
	\@mkboth{\MakeUppercase\bibname}{\MakeUppercase\bibname}%
	\addcontentsline{toc}{chapter}{References}
	\list{\@biblabel{\@arabic\c@enumiv}}%
	{\settowidth\labelwidth{\@biblabel{#1}}%
		\leftmargin\labelwidth
		\advance\leftmargin\labelsep
		 \setlength{\baselineskip}{16pt}
		\setlength{\parsep}{-0.5mm}
		\setlength{\labelsep}{0.5em}
		%\setlength{\itemsep}{0.5pc}
		\setlength{\listparindent}{0in}
		\setlength{\itemindent}{0in}
		\setlength{\rightmargin}{0in}
		\@openbib@code
		\usecounter{enumiv}%
		\let\p@enumiv\@empty
		\renewcommand\theenumiv{\@arabic\c@enumiv}}%
	\sloppy
	\clubpenalty4000
	\@clubpenalty \clubpenalty
	\widowpenalty4000%
	\sfcode`\.\@m}
{\def\@noitemerr
	{\@latex@warning{Empty `thebibliography' environment}}%
	\endlist}



%%附录
%\let\@appendix\appendix
%\renewenvironment{appendix}{%
%  \@appendix
%  \gdef\@chapapp{\appendixname~\thechapter}
%  %\renewcommand\theequation{\ifnum \c@chapter>\z@ \thechapter-\fi\@arabic\c@equation}
%  }{}

%\newcommand{\mmchapter}{\DLUT@chapter*}



\endinput