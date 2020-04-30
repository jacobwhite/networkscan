function toggle(my_class){
	shown = localStorage.getItem(my_class);
	console.log(my_class + " shown: " + shown);
	down_hosts = document.querySelectorAll("." + my_class);
	if(my_class ==  "chart"){
		down_hosts = document.querySelectorAll(".chartjs-render-monitor");
	}
	down_toggle = document.getElementById(my_class + '_toggle');
	//if (down_toggle.innerHTML == "Shown"){
	if(shown === "1"){
		console.log(my_class + " is 1 setting to 0");
		down_toggle.innerHTML = "Hidden";
		localStorage.setItem(my_class, "0");
	}
	else {
		console.log(my_class + " is 0 setting to 1");
		down_toggle.innerHTML = "Shown";
		localStorage.setItem(my_class, "1");
	}

	down_hosts.forEach( element => {
		if(element.style.display != 'none'){
			element.style.display = 'none';
		}
		else {
			element.style.display = 'block';
		}
	});
}

function hide_class(my_class){
	document.querySelectorAll("." + my_class).forEach(e => {e.style.display = 'none';});
}



