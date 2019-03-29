"use strict";


/*AI类*/
function AI6() {
	var oo = this;

	oo.calculateTime = 1000;	//限制每步棋计算的时间
	oo.outcomeDepth = 14;		//终局搜索深度
	var outcomeCoarse = 15;		//终局搜索模糊模式搜索深度
	var maxDepth;
	var outTime;

	var weight = [6, 11, 2, 2, 3];

	var rnd = [
		{ s: 0, a: 1, b: 8, c: 9, dr: [1, 8] },
		{ s: 7, a: 6, b: 15, c: 14, dr: [-1, 8] },
		{ s: 56, a: 57, b: 48, c: 49, dr: [1, -8] },
		{ s: 63, a: 62, b: 55, c: 54, dr: [-1, -8] }
	];

	oo.history = [[], []];			//历史启发表
	for (var i = 0; i < 2; i++)
		for (var j = 0; j <= 60; j++)
			oo.history[i][j] = [0, 63, 7, 56, 37, 26, 20, 43, 19, 29, 34, 44, 21, 42, 45, 18, 2, 61, 23, 40, 5, 58, 47, 16, 10, 53, 22, 41, 13, 46, 17, 50, 51, 52, 12, 11, 30, 38, 25, 33, 4, 3, 59, 60, 39, 31, 24, 32, 1, 62, 15, 48, 8, 55, 6, 57, 9, 54, 14, 49];




	var hash = new Transposition();//置换表类




	function sgn(n) {//符号函数
		return n > 0 ? 1 : n < 0 ? -1 : 0;
	}

	oo.startSearch = function (m) {//main：开始搜索博弈树：最大最小搜索（估价函数）+alphabeta剪枝+mtd算法调用

		// hash = new Transposition();
		// console.profile('性能分析器一');
		var f = 0;
		if (m.space <= oo.outcomeDepth) {//小于深度就开始搜索(也就是最后的结局阶段了)
			//进行终局搜索
			outTime = (new Date()).getTime() + 600000;//终局搜索就不限时间了
			maxDepth = m.space;
			//console.time("计时器2");
			if (maxDepth >= outcomeCoarse)
				f = alphaBeta(m, maxDepth, -Infinity, Infinity);//alpha-beta剪枝：α=-∞；β=+∞
			else
				f = mtd(m, maxDepth, f);//mtd(f)
			//console.timeEnd("计时器2");
			console.log("终局搜索结果：", maxDepth, m.space, m.side, f * m.side);
			return hash.getBest(m.key);//置换表的getBest方法：
		}

		outTime = (new Date()).getTime() + oo.calculateTime;
		maxDepth = 0;
		//console.time("计时器2");
		try {
			while (maxDepth < m.space) {
				f = mtd(m, ++maxDepth, f);//mtd(f)
				// f = alphaBeta(m, ++maxDepth, -Infinity, Infinity);
				var best = hash.getBest(m.key);
				console.log(maxDepth, f * m.side, best);
			}
		} catch (eo) {
			if (eo.message != "time out")
				throw eo;
		}
		//console.timeEnd("计时器2");
		// console.profileEnd();
		console.log("搜索结果：", maxDepth - 1, m.space, m.side, f * m.side);
		return best;//得到的是最好的步数坐标？
	}




	function evaluation(m) {//估价函数
		var corner = 0, steady = 0, uk = {};//corner占角的可能性；steady稳定子，uk
		for (var i = 0, v, l = rnd.length; v = rnd[i], i < l; i++) {
			if (m[v.s] == 0) {
				corner += m[v.a] * -3;		//次要危险点
				corner += m[v.b] * -3;		//次要危险点
				corner += m[v.c] * -6;		//主要危险点
				continue;
			}
			corner += m[v.s] * 15;		//角点
			steady += m[v.s];		//角也是稳定子

			for (var k = 0; k < 2; k++) {
				if (uk[v.s + v.dr[k]])
					continue;
				var eb = true, tmp = 0;
				for (var j = 1; j <= 6; j++) {
					var t = m[v.s + v.dr[k] * j];
					if (t == 0)
						break;
					else if (eb && t == m[v.s])
						steady += t;		//稳定子
					else {
						eb = false;
						tmp += t;		//稳定子
					}
				}
				if (j == 7 && m[v.s + v.dr[k] * 7] != 0) {
					steady += tmp;
					uk[v.s + v.dr[k] * 6] = true;
				}
			}
		}

		var frontier = 0;		//前沿子
		for (var i = 9; i <= 54; i += (i & 7) == 6 ? 3 : 1) {
			if (m[i] == 0)
				continue;
			for (var j = 0; j < 8; j++)
				if (m[othe.dire(i, j)] == 0) {
					frontier -= m[i];
					break;
				}
		}

		var mobility = (m.nextNum - m.prevNum) * m.side;	//行动力

		var parity = m.space < 18 ? (m.space % 2 == 0 ? -m.side : m.side) : 0;	//奇偶性

		var rv = corner * weight[0] + steady * weight[1] + frontier * weight[2] + mobility * weight[3] + parity * weight[4];
		return rv * m.side;
	}


	function outcome(m) {//终局结果
		var s = m.black - m.white;
		if (maxDepth >= outcomeCoarse)
			return sgn(s) * 10000 * m.side;
		return (s + m.space * sgn(s)) * 10000 * m.side;
	}


	function mtd(m, depth, f) {//MTD(f)算法
		//这个算法是对alphabeta剪枝的优化
		var lower = -Infinity;
		var upper = Infinity;
		do {
			var beta = (f == lower) ? f + 1 : f;	// 确定试探值
			f = alphaBeta(m, depth, beta - 1, beta);	// 进行零宽窗口试探
			if (f < beta)
				upper = f;
			else
				lower = f;
		} while (lower < upper);
		if (f < beta)	// 如果最后一次搜索得到的只是上限，需再搜索一次，确保获得正确的最佳棋步
			f = alphaBeta(m, depth, f - 1, f);
		return f;
	}

	function alphaBeta(m, depth, alpha, beta) {//Alpha-beta剪枝

		if ((new Date()).getTime() > outTime)
			throw new Error("time out");

		var hv = hash.get(m.key, depth, alpha, beta);//置换表的get方法
		if (hv !== false)
			return hv;

		if (m.space == 0)			//棋盘子满
			return outcome(m);	//直接返回终局结果

		othe.findLocation(m);

		if (m.nextNum == 0) {		//判断无棋可走
			if (m.prevNum == 0)		//判断上一步也是无棋可走
				return outcome(m);		//直接返回终局结果
			othe.pass(m);//执行跳过
			return -alphaBeta(m, depth, -beta, -alpha);
		}

		if (depth <= 0) {			//搜索深度到达设置的极限
			var e = evaluation(m);
			hash.set(m.key, e, depth, 0, null);//置换表的set方法
			return e;//到达最深的时候就返回评估值
		}

		var hd = hash.getBest(m.key);//给出的是phashe.best
		if (hd !== null)
			moveToHead(m.nextIndex, hd);//到顶层节点


		var hist = oo.history[m.side == 1 ? 0 : 1][m.space];//历史启发表赋值给history
		var hashf = 1;				//最佳估值类型, 0为精确值, 1为<=alpha, 2为>=beta
		var bestVal = -Infinity;		//记录最佳估值
		var bestAct = null;				//记录最佳棋步
		for (var i = 0; i < m.nextNum; i++) {//不断对下一层进行剪枝搜索
			var n = m.nextIndex[i];
			var v = -alphaBeta(othe.newMap(m, n), depth - 1, -beta, -alpha);
			if (v > bestVal) {
				bestVal = v;
				bestAct = n;
				if (v > alpha) {
					alpha = v;
					hashf = 0;//给出精确值
					moveToUp(hist, n);//回到上层节点
				}
				if (v >= beta) {
					hashf = 2;
					break;		//发生剪枝
				}
			}
		}
		moveToHead(hist, bestAct);//回到顶层节点
		hash.set(m.key, bestVal, depth, hashf, bestAct);//置换表的set方法：bestAct从这里返回的
		return bestVal;//这个感觉和上面的evaluation的最后值是一样的
	}



	function moveToHead(arr, n) {//alphabeta里面用于返回树的顶层
		if (arr[0] == n)
			return;
		var i = arr.indexOf(n);
		arr.splice(i, 1);
		arr.unshift(n);
	}

	function moveToUp(arr, n) {//alphabeta里面用于返回上层节点
		if (arr[0] == n)
			return;
		var i = arr.indexOf(n);
		arr[i] = arr[i - 1];
		arr[i - 1] = n;
	}

}


function Transposition() {//置换表

	var oo = this;

	var HASH_SIZE = (1 << 19) - 1;		//置换单元数为 524287
	var data = new Array(HASH_SIZE + 1);

	oo.set = function (key, eva, depth, flags, best) {

		var keyb = key[0] & HASH_SIZE;
		var phashe = data[keyb];
		if (!phashe)
			phashe = data[keyb] = {};
		else if (phashe.key == key[1] && phashe.depth > depth)		//局面相同 并且 记录比当前更深 则不替换
			return;
		phashe.key = key[1];
		phashe.eva = eva;
		phashe.depth = depth;
		phashe.flags = flags;
		phashe.best = best;
	}

	oo.get = function (key, depth, alpha, beta) {
		var phashe = data[key[0] & HASH_SIZE];
		if ((!phashe) || phashe.key != key[1] || phashe.depth < depth)
			return false;
		switch (phashe.flags) {
			case 0:
				return phashe.eva;
			case 1:
				if (phashe.eva <= alpha)
					return phashe.eva;
				return false;
			case 2:
				if (phashe.eva >= beta)
					return phashe.eva;
				return false;
		}
	}

	oo.getBest = function (key) {
		var phashe = data[key[0] & HASH_SIZE];
		if ((!phashe) || phashe.key != key[1])
			return null;
		return phashe.best;
	}
}

