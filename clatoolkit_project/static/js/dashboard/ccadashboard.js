/**
 * ccadashboard.js
 * Authour: Koji Nishimoto
 * Created: 12/09/2016
 */

/**
 * Chart root tags.
 * This contains all charts and tables of a platform.
 * @type {string}
 */
var chartRootTags = "<div class='row' >"
    			+ "<div class='col-lg-12'>"
				+ "<div class='panel panel-default'>"
            	+ "<div class='panel-heading'>"
                + "<i class='fa fa-bar-chart-o fa-fw'></i> "
            	+ "</div>"
            	+ "<div class='panel-body scrollable'>"
                + "<div id='chart-'></div>" //id needs to be added dynamically e.g. "chart-Facebook"
            	+ "</div></div></div></div>";

/**
 * Datatable tags.
 * These are used to show a table. 
 * When a table is required, the tags are aded to chartRootTags.
 * @type {string}
 */
var tableTags = "<div class='tableDiv'>"
				+ "<table class='table table-striped table-bordered table-hover' id='datatable-'></table>"
				+ "</div>";

/**
 * Second Chart tags.
 * This is used to show second 
 * @type {string}
 */
var additionalChartTag = "<div class='panel-body scrollable'>"
				//id needs to be added dynamically e.g. "additionalChart-Facebook". 
				//If necessary, other attributes (class, etc.) will be added dynamically
				+ "<div id='additionalChart-'></div>" 
				+ "</div>";

/**
 * Clear tag.
 * This clears float property in CSS.
 * This is added right before the chartRootTags to clear CSS float property
 * when previous chart is pie or the current chart is odd-numbered chart.
 *
 * @type {string}
 */
var clearTag = "<div class='clear'></div>";


/**
 * Initialise HighCharts charts options.
 */
function initTimeseriesChartOptions() {

	platformSeriesOps = {
		chart: {
			renderTo: "platform_pageview_chart"
		},
		rangeSelector : {
		  selected : 1
		},
		xAxis: {
			events: {
				setExtremes: function (e) {
					$('#report').html('<b>Date From: </b>' + Highcharts.dateFormat('%Y-%m-%d', e.min) +
					' To: ' + Highcharts.dateFormat('%Y-%m-%d', e.max));// + ' | e.trigger: ' + e.trigger);
				}
			}
		},
		tooltip: {
		  style: { width: '200px' },
		  valueDecimals: 0
		},
		yAxis : {
		  min: 0,
		  title : { text : 'Activity' }
		},
		legend: {
		  enabled: true
		},
		series: []
	};
}

/**
 * Show platform timeseries chart
 */
function showPlatformTimeseries() {


	$.ajax({
 		type: "GET",
		url: "/dashboard/api/get_platform_timeseries/?course_code=PROJ-TEAM"
		// url: "/static/js/test/platformtimeseries.json"
	})
	.fail(function(data,textStatus, errorThrown){
    	console.log('error!\r\n' + errorThrown);
	})
	.done(function( data ) {

		// console.log(data);
		initTimeseriesChartOptions();
		// Create series
		$.each(data["series"], function(key,value) {
            var series = { data: []};
            // console.log(value);
            $.each(value, function(key,val) {
                if (key == 'name') { series.name = val; }
                else if(key == 'id') { series.id = val; }
                else {
                    $.each(val, function(key,val) {
                        var d = val.split(",");
                        //Date needs to be converted to UTC for HighCharts...
                        var x = Date.UTC(d[0], d[1], d[2]);
                        series.data.push([x, parseFloat(d[3])]);
                    });
                }
            });
            platformSeriesOps.series.push(series);
        });

		//Note: StockChart() method needs to be called instead of calling Chart()
    	new Highcharts.StockChart(platformSeriesOps, function (chart) {
			// This code is for showing multiple series in the navigator (the mini-chart)
			for(var i = 0; i < chart.options.series.length; i++) {
				chart.addSeries({
				    data: chart.options.series[i].data,
				    isInternal: true,
				    xAxis: 1,
				    yAxis: 1,
				    name: null, 
				    enableMouseTracking: false, 
				    showInLegend: false,
				    color: chart.series[i].color
				});
			}
		});

	});// End of .done(function( data ) {
}

/**
 * Show a chart and a table.
 * Data is retrieved from the web server.
 * 
 * @param {String} platform Platform name
 */
function showCharts(platform) {
	$.ajax({
		url: "/static/js/test/stackedbar" + platform + ".json?platform=" + platform
		// url: "/dashboard/api/get_platform_activity/?platform=" + platform
	})
	.fail(function(data,textStatus, errorThrown){
    	console.log('Error has occurred in showCharts() function. PlatformName: ' + platform + ".\r\n" + errorThrown);
	})
	.done(function( data ) {
		drawChart(platform, data);
		if (data["chart2"]) {
			// showStackedBar("Trello", trData);
			// drawChart(platform, data);
			console.log("Log: object chart2 exists.");
		} else {
			showTable(platform, data);
		}
	});
}

/**
 * Draw chart.
 * 
 * @param {String} platform Platform name
 * @param {Object} data 	Chart data
 */
function drawChart(platform, data) {
	var chart = data["chart"];
	$('#chart-' + platform).highcharts({
		chart: {
			type: chart["type"]
		},
		title: {
			text: chart["title"]
		},
		yAxis: {
        	min: 0,
			allowDecimals: false,
			title: {
			    text: chart["yAxis"]["title"]
			},
            stackLabels: {
                enabled: true,
                style: {
                    fontWeight: 'bold',
                    color: (Highcharts.theme && Highcharts.theme.textColor) || 'black'
                }
            }
		},
		xAxis: {
			categories: chart["categories"]
		},

        series: chart["series"],
        tooltip: {
            headerFormat: '<b>{point.x}</b><br/>',
            pointFormat: '{series.name}: {point.y}<br/>Total: {point.stackTotal}'
        },
        plotOptions: {
            column: {
                stacking: 'normal',
                dataLabels: {
                    enabled: true,
                    color: (Highcharts.theme && Highcharts.theme.dataLabelsColor) || 'white',
                    style: {
                        textShadow: '0 0 3px black'
                    }
                }
            }
        }
	});
}


/**
 * Show table.
 * 
 * @param {String} platform Platform name
 * @param {Object} data 	Chart data
 */
function showTable(platform, data) {

	//Create data columns
	var cate = data["chart"]["categories"];
	var cols = [];
	var ary = {"title": ""};
	cols.push(ary);
	$.each(cate, function(key,val) {
		ary = {"title": val};
		cols.push(ary);
	});
	// console.log(cols);

	//Create table data
	var series = data["chart"]["series"];
	var newData = [];
	ary = [];
	for (var i = 0; i < series.length; i++) {
		ary = series[i]["data"];
		ary.unshift(series[i]["name"]);
		newData.push(ary);
	}
	// console.log("newData" + newData);

	$('#datatable-' + platform).DataTable( {
		bFilter: false,
		bInfo: false,
		bPaginate: false,
		bLengthChange: false,
		bSort: false,
		scrollX: true,
		// scrollY: 200, //maximum hight of the table
		data: newData,
		columns: cols
	});
}

/**
 * Load function.
 */
$(document).ready(function(){

	//TODO: panel-heading (platform name) needs to be set dynamically


	//Show charts and tables
	showPlatformTimeseries();

	//TODO: Get platform name available in the unit from the server
	var platforms = ["Trello"];
	$.each(platforms, function(key,val) {
		showCharts(val);
	});

	//TODO: Get data from the CAL toolkit server
	// trData = getData("Trello");
	// fbData = getData("Facebook");
	// ghData = getData("GitHub");

	// showTable("Trello", trData);
	// showStackedBar("Trello", trData);
	// showTable("GitHub", ghData);
	// showStackedBar("GitHub", ghData);
	// showStackedBar("Facebook", fbData);
	// showPieCharts("Facebook", fbData);
	
	// function showTable(platformName, data) {
	// 	console.log(data["table"]["columns"]);
	// 	$('#datatable-' + platformName).DataTable( {
	// 		bFilter: false,
	// 		bInfo: false,
	// 		bPaginate: false,
	// 		bLengthChange: false,
	// 		bSort: false,
	// 		scrollX: true,
	// 		data: data["table"]["data"],
	// 		columns: data["table"]["columns"]
	// 	});
	// }
	// $('#datatable-trello').dataTable().fnDestroy();

	function showPieCharts(platformName, data) {
		$('#pie-' + platformName).highcharts({

			chart: {
				type: 'pie', //data["chart2"]["type"]
				// plotBorderColor: 'gray',
				// plotBorderWidth: 1,
				// width: $('#chart-' + platformName).width()
				//TODO: width needs to be calculated automatically and defined.
				//Width = 100(first pie position) + 200 * (element number(start at 0) + 1)
				width: parseInt($('#chart-' + platformName).width()) > 900 ? parseInt($('#chart-' + platformName).width()) : 900
			},
			title: {
				text: "Cognitive Presence Classifications",//data["chart2"]["title"],
	            align: 'center',
	            verticalAlign: 'top'
			},
			// When  xAxis is used, click event won't work as expected.
			// (all items in pie chart will be disappeared at once even if you click one of them in the legend)
			// xAxis: {
			// 	categories: ['Triggering', 'Exploration', 'Integration', 'Resolution'];
			// },
	        labels: {
	            style: {
	                // color: '#3E576F',
	                fontSize: '14px'
	            },
	            items:  [
	            	{ html: 'Member 1', style: { left: '130px', top: '60px' }},
	            	{ html: 'Member 2', style: { left: '360px', top: '60px' }},
	            	{ html: 'Member 3', style: { left: '590px', top: '60px' }},
	            	{ html: 'Member 4', style: { left: '820px', top: '60px' }},
	            	{ html: 'Member 5', style: { left: '1050px',top: '60px' }}
	            ]
	            //data["chart2"]["labels"]["items"]
	        },
	        series: [
	        	{
		            type: 'pie',//data["chart2"]["type"],
		            name: 'Member 1',//data["chart2"]["series"]["name"]
		            center: [150, null],//[parseInt(chart2["series"]["size"]["x"]), null],
		            size: 180,
		            dataLabels: {
						enabled: false
					},
		            showInLegend: true,
		            data: [['Triggering', 45.0], ['Exploration', 26.8], ['Integration',12.8], ['Resolution', 8.5]]//data["chart2"]["series"]["data"]
		         //    title: {
			        //     // align: 'left',
			        //     // x: 0
			        //     style: { color: 'black' },
			        //     align: 'center',
			        //     text: '<b>Pie 1</b><br>Subtext',
			        //     verticalAlign: 'top',
			        //     y: -40
			        // }
	        	},{
		            type: 'pie',
		            name: 'Member 2',
		            center: [380, null],
		            size: 180,
		            dataLabels: {
						enabled: false
					},
		            data: [['Triggering', 12.0], ['Exploration', 34.2], ['Integration',22.4], ['Resolution', 31.4]]
	        	},{
		            type: 'pie',
		            name: 'Member 3',
		            center: [610, null],
		            size: 180,
		            dataLabels: {
						enabled: false
					},
		            data: [['Triggering', 45.0], ['Exploration', 26.8], ['Integration',12.8], ['Resolution', 8.5]]
	        	},{
		            type: 'pie',
		            name: 'Member 4',
		            center: [840, null],
		            size: 180,
		            dataLabels: {
						enabled: false
					},
		            data: [['Triggering', 67.0], ['Exploration', 18.5], ['Integration',4.7], ['Resolution', 9.8]]
	        	},{
		            type: 'pie',
		            name: 'Member 5',
		            center: [1070, null],
		            size: 180,
		            dataLabels: {
						enabled: false
					},
		            data: [['Triggering', 29.9], ['Exploration', 32.1], ['Integration',35.4], ['Resolution', 2.6]]
	        	}
	        ],
	        tooltip: {
	        	//NOTE: point.y is actual value tha is set to the pie chart. point.percentage is automatically caluculated by highcharts.
	            // pointFormat: '{point.name}: <b>{point.percentage:.1f}%</b>'
	            formatter: function() {
	            	// console.log(this.series);
			        return '<b>' + this.series.name + '</b><br><b>' + this.point.name + ': ' + this.point.y + '</b>';
			    }
	        },
	        plotOptions: {
	            pie: {
	                allowPointSelect: true,
	                cursor: 'pointer'
	            }
	        }
	    },function(chart) {
	        $(chart.series[0].data).each(function(i, e) {
	            e.legendGroup.on('click', function(event) {
	                var legendItem=e.name;
	                event.stopPropagation();
	                $(chart.series).each(function(j,f){
	                       $(this.data).each(function(k,z){
	                           if(z.name==legendItem) {
	                               if(z.visible) {
	                                   z.setVisible(false);
	                               } else {
	                                   z.setVisible(true);
	                               }
	                           }
	                       });
	                });//End of $(chart.series).each(function(j,f)
	            });
	        });// End of $(chart.series[0].data).each(function(i, e)
		});
	}

	function getData(platformName) {
		
		//Note: This is test data
		//TODO: Get data from the CAL toolkit server
		platformData = [];
		if (platformName == "Trello") {
			//Note: Data should be the total number of table data?
			// table = [];
			// table["data"] = [['Tasks responsible for', 1,2,6,2,4,5,2,6,8,3], ['Tasks resolved', 2,0,4,5,9,7,2,3,5,6]];
			// table["columns"] = [
			// 		{ title: ""},
			// 		{ title: "Member 1"},
			// 		{ title: "Member 2"},
			// 		{ title: "Member 3"},
			// 		{ title: "Member 4"},
			// 		{ title: "Member 5"},
			// 		{ title: "Member 6"},
			// 		{ title: "Member 7"},
			// 		{ title: "Member 8"},
			// 		{ title: "Member 9"},
			// 		{ title: "Member 10"}
			// 		//
			// 		// [""],["Member 1"], ["Member 2"], ["Member 3"], ["Member 4"], ["Member 5"],
			// 		// ["Member 6"], ["Member 7"], ["Member 8"], ["Member 9"], ["Member 10"]
			// 	];
			// chart = [];
			// chart["data"] = [{name: 'Tasks responsible for', data:[1,2,6,2,4,5,2,6,8,3]}, {name: 'Tasks resolved', data: [2,0,4,5,9,7,2,3,5,6]}];
			// chart["categories"] = ['Member 1', 'Member 2', 'Member 3', 'Member 4', 'Member 5', 'Member 6', 'Member 7', 'Member 8', 'Member 9', 'Member 10'];
			// chart["type"] = "column";
			// chart["title"] = "Group 1";
			// chart["yAxisTitle"] = "Units";
			// // chart["name"] = "Group 1 members";
			// platformData["table"] = table;
			// platformData["chart"] = chart;
		}
		else if (platformName == "Facebook") {

			//TODO: What kinda of data is shown in bar chart on FB?
			table = [];
			table["data"] = [['Assigned inquiry based task', 12,15,6,21,18]];
			table["columns"] = [
					{ title: ""},
					{ title: "Member 1"},
					{ title: "Member 2"},
					{ title: "Member 3"},
					{ title: "Member 4"},
					{ title: "Member 5"}
				];
			chart = [];
			chart["data"] = [{name: 'Assigned inquiry based task', data:[12,15,6,21,18]}];
			chart["categories"] = ['Member 1', 'Member 2', 'Member 3', 'Member 4', 'Member 5'];
			chart["type"] = "column";
			chart["title"] = "Group 1";
			chart["yAxisTitle"] = "%";
			chart["name"] = "Group 1 members";
			platformData["table"] = table;
			platformData["chart"] = chart;
		} 
		else if (platformName == "GitHub") {
			
			// //Note: Data should be the total number of table data?
			// table = [];
			// table["data"] = [['Additions', 501,427,281,615], ['Deletions', 291,58,102,93]
			// 				// , ['Test1',10,41,15,6], ['Test2', 32,37,49,12], ['Test3',10,41,15,6], ['Test4', 32,37,49,12]
			// 			];
			// table["columns"] = [
			// 		{ title: ""},
			// 		{ title: "Member 1"},
			// 		{ title: "Member 2"},
			// 		{ title: "Member 3"},
			// 		{ title: "Member 4"}
			// 	];
			// chart = [];
			// chart["data"] = [{name: 'Additions', data:[501,427,281,615]}, {name: 'Deletions', data: [291,58,102,93]}
			// 				// ,{name: 'Test1', data:[10,41,15,6]}, {name: 'Test2', data: [32,37,49,12]},
			// 				// {name: 'Test3', data:[10,41,15,6]}, {name: 'Test4', data: [32,37,49,12]}
			// 			];
			// chart["categories"] = ['Member 1', 'Member 2', 'Member 3', 'Member 4'];
			// chart["type"] = "column";
			// chart["title"] = "Web App Developers";
			// chart["yAxisTitle"] = "Units";
			// // chart["name"] = "Developers";
			// platformData["table"] = table;
			// platformData["chart"] = chart;
		}
		return platformData;
	}
});
