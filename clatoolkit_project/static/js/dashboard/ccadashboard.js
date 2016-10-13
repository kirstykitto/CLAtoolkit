/**
 * ccadashboard.js
 * Authour: Koji Nishimoto
 * Created: 12/09/2016
 */

/**
 * Inner pie chart diameter
 * It is used for a donut pie chart.
 * @type {Number}
 */
var PIE_DIAMETER_INNER = 140;

/**
 * Outer pie chart diameter
 * It is used for a single pie chart.
 * @type {Number}
 */
var PIE_DIAMETER_OUTER = 270;

/**
 * First pie chart's position X
 * @type {Number}
 */
var PIE_INIT_POSITION_X = 140;

/**
 * Distance between next pie chart
 * @type {Number}
 */
var PIE_OFFSET = 410;

/**
 * Brightness of chart color
 * @type {Number}
 */
var CHART_COLOR_BRIGHTNESS = 0.2;

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
				// Navigator range changed event handler
				afterSetExtremes: function (e) {
					// startDate = Highcharts.dateFormat('%Y,%m,%d', e.min);
					// endDate = Highcharts.dateFormat('%Y,%m,%d', e.max);
					// e.preventDefault();
					// console.log(startDate);
					// console.log(endDate);
					if(allPlatformData != null) {
						var platformNames = platform.split(",");
						$.each(platformNames, function(key, val) {
							chartData = createChartSeries(allPlatformData[val], true, e.min, e.max);
							if(chartData != null) {
								allPlatformData[val] = chartData;
								drawGraphs(chartData);
								showAllTables(chartData);
							}
						});
					}
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
		url: "/dashboard/api/get_platform_timeseries_data/?course_code=" + course_code + "&platform=" + platform
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
	if(platform == undefined || platform == "None" || platform == "" || platform.length == 0) {
		showMessage('Error: No platforms found. Charts and tables could not be generated.');
		return;
	}
	$.ajax({
		url: "/dashboard/api/get_platform_activities/?course_code=" + course_code + "&platform=" + platform
	})
	.fail(function(data, textStatus, errorThrown){
    	console.log('Error has occurred in showCharts() function. PlatformName: ' + platform + ".\r\n" + errorThrown);
	})
	.done(function( data ) {
		chartData = createChartSeries(data, false, null, null)
		allPlatformData[platform] = chartData;
		drawGraphs(chartData);
		showAllTables(chartData);
		// allPlatformData = chartData;
	});
}

/**
 * Create series for charts.
 * Sample series that will be created is shown below. (for bar chart)
	"series": [{
			"name": "created", 
			"data":[1,2,6,2,4,5,2,6,8,3]
		}, {
			"name": "updated", 
			"data": [2,0,4,5,9,7,2,3,5,6]
	}]
 * @param  {[Object]} data JSON data for charts
 * @param  {[boolean]} checkDate if true, data between start date and end date that user selected in the navigator 
 *                               at the Platform Timeseries, will be returned.
 */
function createChartSeries(data, checkDate, start, end) {
	if(data == null || data["platforms"] == null) {
		return null;
	}
	$.each(data["platforms"], function(key, val) {
		$.each(val["charts"], function(key, chart) {
			// var chart = val["charts"][0];
			var allSeries = null;
			switch(chart['type']) {
				case 'column':
					chart["series"] = createBarChartSeries(chart, checkDate, start, end);
					break;
				case 'pie':
					chart["series"] = createPieChartSeries(chart, false, checkDate, start, end);
					break;
				default:
					break;
			}
		});
	});
	return data;
}


function createPieChartSeries(chart, isDetailChart, checkDate, start, end, colors) {
	var allSeries = [];
	if (colors == null || colors.length == 0) {
		colors = createChartColors(chart["seriesName"]);
	}

	posX = PIE_INIT_POSITION_X;
	$.each(chart["categories"], function(key, cate) {
		if (parseInt(key) > 0) {
			posX += PIE_OFFSET;
		}

		dataset = [];
		$.each(chart["seriesName"], function(key, seriesName) {
			var userData = chart["data"].filter(function(item, index){
			  if (item["category"] == cate) return true;
			});
			var series = userData[0]["series"].filter(function(item, index) {
				if (item["name"] == seriesName) return true;
			});

			var total = 0;
			if(series.length > 0) {
				if(checkDate) {
					$.each(series[0]["date"], function(key, value) {
	                    var d = value.split(",");
	                    var utcDate = Date.UTC(d[0], d[1], d[2]);
						// Add value when startDate <= value >= endDate
						if(parseFloat(start) <= parseFloat(utcDate) && parseFloat(end) >= parseFloat(utcDate)) {
							total += series[0]["values"][key];
						}
					});
				} else {
					// Add up all values of the current series
					$.each(series[0]["values"], function(key , value) {
						total += value;
					});
				}
			}
			
			var newData = {
				name: seriesName,
				y: total
			};
			if(!isDetailChart) {
				newData["color"] = getChartColorByName(colors, seriesName, true);
			}
			else if(isDetailChart && series.length > 0) {
				// Color of each piece of outer pie is similar to that of collesponding inner piece
				var verb = null;
				$.each(chart["objectMapper"], function(key, element) {
					if ($.inArray(seriesName, element) != -1) {
						verb = key;
						return true;
					}
				});

				newData["color"] = getChartColorByName(colors, verb, false);
			}
			dataset.push(newData);
		});
		colorIndex = 0;
		diameter = isDetailChart ? PIE_DIAMETER_OUTER : PIE_DIAMETER_INNER;
		var newSeries = {
			type: chart['type'],
			name: cate,
			center: [posX, null],
			size: diameter,
			// dataLabels: {enabled: false},
			dataLabels:{
				formatter: function () {
					// return this.y > 0 ? '<b>' + this.point.name + '</b>' : null;
					return this.y > 0 ? this.point.name : null;
				},
				distance: -20
			},
			data: dataset
		}
		if(isDetailChart) {
			// newSeries["size"] = PIE_DIAMETER_OUTER;
			newSeries["innerSize"] = PIE_DIAMETER_INNER;
			newSeries["dataLabels"] = {
				formatter: function () {
					return this.y > 0 ? '<b>' + this.point.name + ': ' + this.y + '</b>' : null;
				},
				distance: -5
			};
		}
		allSeries.push(newSeries);
	});

	if(chart["detailChart"]) {
		chart["detailChart"]["series"] = createPieChartSeries(chart["detailChart"], true, checkDate, start, end, colors);
	}
	return allSeries;
}


function getChartColorByName(colors, seriesName, isBrighter) {
	var series = colors.filter(function(item, index) {
		if (item["name"] == seriesName) return true;
	});
	// return Highcharts.Color(series[0]["color"]).brighten(0.4).get();
	color = series[0]["color"];
	if(isBrighter) {
		color = Highcharts.Color(series[0]["color"]).brighten(CHART_COLOR_BRIGHTNESS).get();
	}
	return color;
}


function createChartColors(series) {
	var colors = Highcharts.getOptions().colors;
	var colorIndex = 0;
	var ret = [];
	$.each(series, function(key, name) {
		obj = { name: name, color: colors[colorIndex % colors.length] };
		ret.push(obj);
		colorIndex++;
	});
	return ret;
}


function createBarChartSeries(chart, checkDate, start, end) {
	var allSeries = [];
	$.each(chart["seriesName"], function(key, seriesName) {
		obj = [];
		$.each(chart["categories"], function(key, cate) {
			// Search current category (user name, etc.) and series (verb, etc.) in chart["data"]
			var userData = chart["data"].filter(function(item, index){
			  if (item["category"] == cate) return true;
			});
			var series = userData[0]["series"].filter(function(item, index) {
				if (item["name"] == seriesName) return true;
			});

			var total = 0;
			if(series.length > 0) {
				if(checkDate) {
					$.each(series[0]["date"], function(key, value) {
	                    var d = value.split(",");
	                    var utcDate = Date.UTC(d[0], d[1], d[2]);
						// Add value when startDate <= value >= endDate
						if(parseFloat(start) <= parseFloat(utcDate) && parseFloat(end) >= parseFloat(utcDate)) {
							total += series[0]["values"][key];
						}
					});
				} else {
					// Add up all values of the current series
					$.each(series[0]["values"], function(key , value) {
						total += value;
					});	
				}
			}
			obj.push(total);
		});
		var newSeries = {
			name: seriesName,
			data: obj
		};
		allSeries.push(newSeries);
	});

	return allSeries;
}

/**
 * Draw all .
 * 
 * @param {Object} data 	Chart data
 */
function drawGraphs(data) {
	$.each(data["platforms"], function(key , val) {
		$.each(val["charts"], function(key , chart) {
			// Show graph area
			changeChartAreaVisibility(true, val["platform"]);
			if ($('#' + chart['type'] + '-' + val["platform"]).highcharts()) {
				$('#' + chart['type'] + '-' + val["platform"]).highcharts().destroy();
			}
			switch(chart['type']) {
				case 'column':
					drawBarChart(chart, val["platform"]);
					break;
				case 'pie':
					// Draw single/inner pie chart
					// Note that outer pie has not been drawn yet
					drawPieChart(chart, val["platform"]);
					if(chart["detailChart"]) {
						$.each(chart["detailChart"]["series"], function(key, series) {
							// To draw outer pie, add outer pie series to chart
							addSeriesToChart(series, chart['type'], val["platform"]);
						});
					}
					break;
				default:
					break;
			}
		});
	});
}

function changeChartAreaVisibility(showChartArea, platform) {
	if(showChartArea) {
		$("#chartRoot-" + platform).show();
	} else {
		$("#chartRoot-" + platform).hide();
	}
}

function addSeriesToChart(series, chartType, platform) {
	var chart = $('#' + chartType + '-' + platform).highcharts();
	chart.addSeries(series);
}

function calculateChartAreaWidth(chart) {
	// Pie size * num of categories
	var areaWidth = (chart["categories"].length * PIE_DIAMETER_OUTER);
	// Add offset width between pies
	areaWidth += (chart["categories"].length - 1) * (PIE_OFFSET - PIE_DIAMETER_OUTER);
	// Add Initial position X and subside a little bit to adjust the width
	areaWidth += PIE_INIT_POSITION_X - 30;
	return areaWidth
}


function getChartLabels(categories) {
	var items = [];
	var left = PIE_INIT_POSITION_X - 30;
	var index = 0;
	$.each(categories, function(key, cate) {
		if(key > 0) {
			left += PIE_OFFSET;
		}
		label = {
			html: cate,
			style: { left: left, top: 10 }
		}
		items.push(label);
	});
	return items;
}


/**
 * Draw pie chart.
 * @param  {[type]} chart [description]
 * @return {[type]}       [description]
 */
function drawPieChart(chart, platform) {
	chartWidth = calculateChartAreaWidth(chart);
	labelItems = getChartLabels(chart["categories"]);
	$('#' + chart['type'] + '-' + platform).highcharts({
		chart: {
			type: chart["type"],
            // width: parseInt($('#column-' + platform).width()) > 900 ? parseInt($('#column-' + platform).width()) : 900
            width: chartWidth
		},
		title: {
			text: " ",
            align: 'center',
            verticalAlign: 'top'
		},
        labels: {
            style: {
                // color: '#3E576F',
                fontSize: '20px'
            },
            // items:  [
            //     { html: 'Member 1', style: { left: 120, top: 10 }},
            //     { html: 'Member 2', style: { left: 530, top: 10 }},// left = offset - 20
            //     { html: 'Member 3', style: { left: 940, top: 10 }},
            //     // { html: 'Member 4', style: { left: '820px', top: '60px' }},
            //     // { html: 'Member 5', style: { left: '1050px',top: '60px' }}
            // ]
            items: labelItems
        },
        tooltip: {
            //NOTE: point.y is actual value tha is set to the pie chart. point.percentage is automatically caluculated by highcharts.
            // pointFormat: '{point.name}: <b>{point.percentage:.1f}%</b>'
            // formatter: function() {
            //     // console.log(this.series);
            // 	pointFormat: '{series.name}: {point.y}<br/>Total: {point.stackTotal}'
            //     // return '<b>' + this.point.name + ': ' + this.point.y + '</b>';
            // }
            // pointFormat: 'Activity: {point.name}: Total: {point.y}<br/>'
            formatter: function() {
				format = '<b>' + this.series.name + '</b><br>'
				+ '<b>' + this.point.name + ': ' + this.point.y + '</b>';
				return format;
            }
        },
        plotOptions: {
            pie: {
                // allowPointSelect: true,
                cursor: 'pointer'
            }
        },
        series: chart["series"]
	});
}

/**
 * Draw bar chart.
 * @param  {[type]} chart [description]
 * @return {[type]}       [description]
 */
function drawBarChart(chart, platform) {
	$('#' + chart['type'] + '-' + platform).highcharts({
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
			    text: chart['yAxis']["title"]
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
 * Show all tables in CCA dashboard.
 * 
 * @param {Object} data 	Chart data
 */
function showAllTables(data) {
	$.each(data["platforms"], function(key , val) {
		$.each(val["charts"], function(key , chart) {
			showTable(chart, val["platform"]);
			// Show table of details chart (outer pie, drilldown bar, etc.)
			showTable(chart["detailChart"], val["platform"]);
		});
	});
}

function showTable(chart, platform) {
	if (chart == null) return;
	// In $.each(), keyword "continue" does not work. 
	// Return anything that's not false and it will behave as a continue. 
	// Return false, and it will behave as a break:
	if(parseInt(chart["showTable"]) != 1) return true;

	//TODO: Code needs to be modified for other type of charts 
	//Create data columns
	var cate = chart["categories"];
	var cols = [];
	var ary = {"title": ""};
	cols.push(ary);
	$.each(cate, function(key, val) {
		ary = {"title": val};
		cols.push(ary);
	});

	//Create table data
	newData = getTableData(chart);
	var elemName = chart["type"] + "-" + platform;
	if ($('#datatable-' + elemName).dataTable.isDataTable()) {
		$('#datatable-' + elemName).dataTable.fnDestroy();
	}
	$('#datatable-' + elemName).DataTable( {
		bFilter: false,
		bInfo: false,
		bPaginate: false,
		bLengthChange: false,
		bDestroy: true, //To reinitialise datatable, this has to be true.
		bSort: false,
		scrollX: true,
		// scrollY: 200, //maximum hight of the table
		data: newData,
		columns: cols
	});
}


function getTableData(chart) {
	var series = chart["series"];
	var newData = [];
	ary = [];
	if(chart["type"] == "pie") {
		var dataSet = {}
		$.each(chart["seriesName"], function(key, elem) {
			dataSet[elem] = [];
		});

		$.each(series, function(key, val) {
			$.each(val["data"], function(key, data) {
				values = dataSet[data["name"]];
				values.push(data["y"]);
				dataSet[data["name"]] = values;
			});
		});

		$.each(dataSet, function(key, val) {
			ary.push(key);
			$.merge(ary, val)
			newData.push(ary);
			ary = [];
		});
	} else {
		$.each(series, function(key, val) {
			ary.push(val["name"]);
			$.merge(ary, val["data"])
			newData.push(ary);
			ary = [];
		});
	}
	return newData;
}


/**
 * Show message.
 * @param  {[String]} message Message to show.
 */
function showMessage(message) {
	$("#message").append(message);
	$("#message").show();
}

/**
 * Load function.
 */
$(document).ready(function(){
	//Show charts and tables
	var platformNames = platform.split(",");
	$.each(platformNames, function(key, val) {
		allPlatformData[val] = {};
		showCharts(val);
	});
	showPlatformTimeseries();
});
