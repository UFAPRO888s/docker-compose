(function() {
	const param = 'fbclid';
	if (location.search.indexOf(param + '=') !== -1) {
		let replace = '';
		try {
			let url = new URL(location);
			url.searchParams.delete(param);
			replace = url.href;
		} catch (ex) {
			let regExp = new RegExp('[?&]' + param + '=.*$');
			replace = location.search.replace(regExp, '');
			replace = location.pathname + replace + location.hash;
		}
		history.replaceState(null, '', replace);
	}
	document.addEventListener('DOMContentLoaded', () => {
		let opts = {
			align: 0,
			font: 0,
		}
		if (localStorage.font)
			opts.font = localStorage.font;
		if (localStorage.align)
			opts.align = localStorage.align;

		var update = function(){
			let app = document.getElementById('app');
			app.setAttribute("font", opts.font);
			app.setAttribute("talign", opts.align);
		};
		update();

		document.getElementById('btn-toggle-align').addEventListener('click', () => {
			opts.align = (opts.align + 1) % 2;
			if(isNaN(opts.align))
				opts.align = 0;
			localStorage.align = opts.align;
			update();
		});
		document.getElementById('btn-toggle-font').addEventListener('click', () => {
			opts.font = (opts.font + 1) % 3;
			if(isNaN(opts.font))
				opts.font = 0;
			localStorage.font = opts.font;
			update();
		});
	});
})();