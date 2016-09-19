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
		url: "/dashboard/api/get_platform_timeseries/?course_code=" + course_code + "&platform=" + platform
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
		url: "/dashboard/api/get_platform_activity/?course_code=" + course_code + "&platform=" + platform
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
	// console.log(data["activities"]);
	var chart = data["activities"][0]["chart"];
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

	var chartVal = data["activities"][0]["chart"];
	//Create data columns
	var cate = chartVal["categories"];
	var cols = [];
	var ary = {"title": ""};
	cols.push(ary);
	$.each(cate, function(key,val) {
		ary = {"title": val};
		cols.push(ary);
	});
	// console.log(cols);

	//Create table data
	var series = chartVal["series"];
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
	var platforms = [platform];
	$.each(platforms, function(key,val) {
		showCharts(val);
	});
});
