(function ($) {

    'use strict';

    // ------------------------------------------------------- //
    // Vertical Bar 02
    // ------------------------------------------------------ //	
	var ctx = document.getElementById("vertical-chart-02").getContext('2d');
	
	var myChart = new Chart(ctx, {
		type: 'bar',
		data: {
			labels: ["Sep", "Oct", "Nov", "Dec", "Jan", "Feb"],
			datasets: [{
				label: 'Incomes',
				data: [150, 120, 130, 100, 80, 50],
                borderColor: "#fff",
				backgroundColor: "rgba(93, 83, 134, 0.85)",
				hoverBackgroundColor: "#5d5386"
			}, {
				label: 'Expenses',
				data: [120, 150, 80, 140, 45, 80],
				borderColor: "#fff",
				backgroundColor: "#e4e8f0",
				hoverBackgroundColor: "#dde1e9"
			}]	
		},
		options: {
		    responsive: false,
			legend: {
				display: true,
				position: 'top',
				labels: {
					fontColor: "#2e3451",
					usePointStyle: true,
					fontSize: 13
				}
			},
            tooltips: {
                backgroundColor: 'rgba(47, 49, 66, 0.8)',
                titleFontSize: 13,
                titleFontColor: '#fff',
                caretSize: 0,
                cornerRadius: 4,
                xPadding: 10,
                displayColors: false,
                yPadding: 10
            },
			scales: {
				xAxes: [{
					stacked: false,
					gridLines: {
						drawBorder: true,
						display: true
					},
					ticks: {
						display: true
					}
				}],
				yAxes: [{
					stacked: false,
					gridLines: {
						drawBorder: true,
						display: true
					},
					ticks: {
						display: true
					}
				}]
			}	
		}
	});
	
})(jQuery);
