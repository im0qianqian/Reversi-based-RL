"use strict";

/*棋盘类*/
function Chessboard() {
	var oo = this;

	var pieces;		//棋子元素
	var piecesnum;	//黑白子数目显示元素
	var side;	//表示执棋方元素

	oo.toDown = null;	//下子

	function bindEvent(td) {	//绑定点击事件
		for (var i = 0; i < 64; i++)
			(function (i) {
				td[i].onclick = function () {
					if (pieces[i].className == "prompt")//标签中可以走的位置已被标记 prompt
						oo.toDown(i);//下棋的指令
				}
			})(i);
		td = undefined;
	}

	oo.create = function (toDown = null) {		//创建棋盘，toDown 为下棋后触发的事件
		oo.toDown = toDown;

		var obj = document.getElementById("chessboard");
		var html = "<table>";//这个地方创建是通过改变html来创建的，使用table创建
		for (var i = 0; i < 8; i++) {
			html += "<tr>";
			for (var j = 0; j < 8; j++)
				html += "<td class='bg" + (j + i) % 2 + "'><div></div></td>";
			html += "</tr>";
		}

		html += "</table>";
		obj.innerHTML = html;
		pieces = obj.getElementsByTagName("div");
		bindEvent(obj.getElementsByTagName("td"));

		piecesnum = document.getElementById("console").getElementsByTagName("span");
		side = {
			"1": document.getElementById("side1"),
			"-1": document.getElementById("side2")
		};
	}

	oo.update = function (map) {//更新显示的棋盘
		//给入map
		for (var i = 0; i < 64; i++)
			pieces[i].className = ["white", "", "black"][map[i] + 1];
		for (var n in map.next)
			pieces[n].className = "prompt";
		for (var i = 0; i < map.newRev.length; i++)
			pieces[map.newRev[i]].className += " reversal";
		if (map.newPos != -1)
			pieces[map.newPos].className += " newest";
		piecesnum[0].innerHTML = map.black;
		piecesnum[1].innerHTML = map.white;
		side[map.side].className = "cbox side";
		side[-map.side].className = "cbox";
	}
}


/* 棋盘逻辑类 */
function Othello() {
	var oo = this;			// oo申明是类本身

	var map = [];			// 棋局数组
	var history = [];		// 历史记录,用于悔棋操作

	oo.aiSide = 0;			// 先行方：1: 电脑为黑棋, -1: 电脑为白棋,  0: 双人对战 2: 电脑自己对战

	var aiRuning = false;	//AI运算中...
	var aiRuningObj = document.getElementById("airuning");		// 也就是指示出现提示框
	var passObj = document.getElementById("pass");				// 没有棋下的时候就返回这个

	var timer;													// 定时器id：局时
	oo.play = function () {										// 开始新棋局：所有的数据初始化都在这里，这个是 main

		if (aiRuning) {		// 如果当前有 ai 在执行则跳出
			return;
		}
		clearTimeout(timer);// 清空计时器

		console.clear();		// 清空控制台下信息，用于调试方便

		// 棋盘初始化
		map = new Array(64).fill(0);	// 空格为 0
		map[28] = map[35] = 1;			// 黑子为 1
		map[27] = map[36] = -1;			// 白子为 -1

		map.black = map.white = 2;		// 黑白棋子数目
		map.space = 60;					// 空格数目（64个格子，但是一开始4个是有东西的了）

		map.frontier = [];				// 当前棋盘上所有棋子临近的空格子
		var tk = [18, 19, 20, 21, 26, 29, 34, 37, 42, 43, 44, 45];//用于初始化的暂存数据
		for (var i = 0; i < tk.length; i++)
			map.frontier[tk[i]] = true;

		map.side = 1;		// 当前执棋方（1.黑棋 0.白棋）
		map.newPos = -1;	// 最新下子的位置
		map.newRev = [];	// 最新反转棋子的位置
		map.nextIndex = [];	// 下一步可走棋的位置
		map.next = {};		// 下一步可走棋的反转棋子
		map.nextNum = 0;	// 下一步可走棋的数目
		map.prevNum = 0;	// 上一步可走棋的数目

		history = [];       // 历史记录

		update();			// update更新上面的初始化数据
	}


	function update() {	//每次更新棋盘：判断是否可走，
		// 如果 AI 是当前持子方或者是电脑自己对战时为 true
		var aiAuto = oo.aiSide == map.side || oo.aiSide == 2;
		oo.findLocation(map);
		setAIRunStatus(false);//不显示ai在计算
		setPassStatus(false);//不显示pass
		board.update(map);//ai下棋：传入map，还有aiAuto函数
		// console.log(map.nextIndex)

		if (map.space == 0 || map.nextNum == 0 && map.prevNum == 0) {//棋盘子满 或 双方都无棋可走
			timer = setTimeout(gameOver, 450);
			return;
		}
		if (map.nextNum == 0) {//无棋可走pass
			timer = setTimeout(function () {
				oo.pass(map);
				update();
				setPassStatus(true);//不显示pass
			}, 450);
			return;
		}
		if (aiAuto) {//也就是当aiAuto是真的时候开始执行
			aiRuning = true;//这个是打一个条幅
			timer = setTimeout(function () {
				setAIRunStatus(true);//AI开始运行
				timer = setTimeout(aiRun, 50);//这个地方就是ai走棋了
			}, 400);
		}
	}

	function aiRun() {
		var request = {};
		var data = new Array();
		for (var i = 0; i < 8; i++) {
			data.push(map.slice(i * 8, i * 8 + 8));
		}
		request['mode'] = 'board';
		request['data'] = JSON.stringify(data);
		request['color'] = map.side;

		// 发送数据
		$.ajax({
			type: "POST",
			url: 'http://localhost:9420',
			data: JSON.stringify(request),
			dataType: "json",
			async: true,
			timeout: 5000,
			success: function (data) {
				if (status == 0) {
					var result = data['response'];
					oo.go(result);
					console.log('Request data success, message = "' + data['message'] + '", result = ', result, ' (', Math.floor(result / 8), ',', result % 8, ')');
				} else {
					console.log('Request data success, but status = 1');
				}
			},
			error: function (data) {
				alert('ajax error', data);
			}
		})
	}


	function gameOver() {//终局的时候
		setAIRunStatus(false);//不显示ai在计算
		setPassStatus(false);//不显示pass
		alert("棋局结束\n\n黑棋: " + map.black + " 子\n白棋: " + map.white + " 子\n\n" + (map.black == map.white ? "平局!!!" : map.black > map.white ? "黑棋胜利!!!" : "白棋胜利!!!"));
	}

	oo.dire = (function () {//获取某一棋盘格某一方向的格子.超过边界返回64
		var dr = [-8, -7, 1, 9, 8, 7, -1, -9];
		var bk = [8, 0, 0, 0, 8, 7, 7, 7];
		return function (i, d) {
			i += dr[d];
			return (i & 64) != 0 || (i & 7) == bk[d] ? 64 : i;
		}
	})();

	oo.findLocation = function (m) {//查找可走棋的位置
		function is(i, j) {
			var lk = 0;
			while ((i = oo.dire(i, j)) != 64 && m[i] == -m.side) {
				ta[la++] = i;
				lk++;
			}
			if (i == 64 || m[i] != m.side)
				la -= lk;
		}
		m.nextIndex = [];
		m.next = [];

		for (var i = 0; i < 64; i++) {
			if (!m.frontier[i])	// 如果与已有棋子不相邻，则这一点一定不是解
				continue;
			var ta = [], la = 0;
			for (var j = 0; j < 8; j++)
				is(i, j);
			if (la > 0) {
				if (la != ta.length)
					ta = ta.slice(0, la);
				m.next[i] = ta;		// 存储棋子 i 所能转换的棋子
				m.nextIndex.push(i);	// 棋子 i 是可行走法
			}
		}
		m.nextNum = m.nextIndex.length;//这个是为了pass使用
	}

	oo.pass = function (m) {//一方无棋可走就pass
		m.side = -m.side;//下棋方
		m.prevNum = m.nextNum;//历史记录次序往后一个
	}



	oo.newMap = function (m, n) {			//返回新的棋局
		//m给入map，n给入下一步棋的位置

		var nm = m.slice(0);
		nm[n] = m.side;
		nm.frontier = m.frontier.slice(0);		//复制数组
		nm.frontier[n] = false;
		for (var i = 0; i < 8; i++) {
			var k = oo.dire(n, i);
			if (k != 64 && nm[k] == 0)
				nm.frontier[k] = true;
		}

		var ne = m.next[n];
		var l = ne.length;
		for (var i = 0; i < l; i++) {
			nm[ne[i]] = m.side;		//反转的棋子
		}

		//下面计算空格数、黑棋数、白棋数
		if (m.side == 1) {
			nm.black = m.black + l + 1;
			nm.white = m.white - l;
		} else {
			nm.white = m.white + l + 1;
			nm.black = m.black - l;
		}

		nm.space = 64 - nm.black - nm.white;		//空格数目
		nm.side = -m.side;
		nm.prevNum = m.nextNum;

		return nm;
	}


	oo.goChess = function (n) {//走棋
		history.push(map);
		oo.go(n);
	}

	oo.go = function (n) {	//走棋，n 代表走棋的位置
		aiRuning = false;

		var rev = map.next[n];	// rev 是走这一步翻转的棋子

		map = oo.newMap(map, n);
		map.newRev = rev;
		map.newPos = n;
		update();
	}

	oo.historyBack = function () {//悔棋功能
		if (aiRuning || history.length == 0)
			return;
		clearTimeout(timer);
		map = history.pop();
		update();
	}

	function setAIRunStatus(t) {//设置AI运算状态
		aiRuningObj.style.display = t ? "block" : "none";
	}

	function setPassStatus(t) {//设置pass状态：无棋可下就pass
		passObj.style.display = t ? "block" : "none";
		if (t) {
			passObj.innerHTML = map.side == 1 ? "白方无棋可下，黑方继续下子" : "黑方无棋可下，白方继续下子";
		}
	}
}

/*main*/
var board = new Chessboard();	// 创建棋盘对象
var othe = new Othello();		// 创建逻辑控制对象
board.create(othe.goChess);		// 棋盘创建，绑定下棋后的事件

document.getElementById("play").onclick = function () {	// 开始 + 重新开始
	document.getElementById("selectbox").style.display = "block";
};

document.getElementById("ok").onclick = function () {	// 点击开始 -> 确定后
	document.getElementById("selectbox").style.display = "none";	// 先隐藏选择框
	var ro = document.getElementById("selectbox").getElementsByTagName("input");	// 获取选择的内容
	if (ro[0].checked) {	// 玩家先手
		othe.aiSide = -1;
	} else if (ro[1].checked) {	// 电脑先手
		othe.aiSide = 1;
	} else if (ro[2].checked) { // 双人模式
		othe.aiSide = 0;
	} else {	// 观战模式
		othe.aiSide = 2;
	}
	othe.play();
};

document.getElementById("cancel").onclick = function () {//取消
	document.getElementById("selectbox").style.display = "none";
};

document.getElementById("back").onclick = function () {//悔棋
	othe.historyBack();
};

document.getElementById("explain").onclick = function () {//最下面解释的弹窗控件
	alert("nothing");
};

document.getElementById("no3d").onclick = function () {//3D棋盘切换
	var desk = document.getElementById("desk");
	desk.className = desk.className == "fdd" ? "" : "fdd";
	this.innerHTML = desk.className == "fdd" ? "2D" : "3D";
};
