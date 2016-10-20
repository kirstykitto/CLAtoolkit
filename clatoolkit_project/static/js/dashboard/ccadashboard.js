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
		drawNavigator(data);
	});// End of .done(function( data ) {
}


function createNavigatorSeries(data) {
	allSeries = [];
	$.each(data["series"], function(key,value) {
		var series = { 
			name : '',
			lineWidth: 0,
			marker: {
				enabled: false,
				states: {
					hover: { enabled: false }
				}
			},
			data : [],
		};

		var seriesData = [];
		$.each(value, function(key,val) {
			if (key == 'name')   { series.name = val; }
			else if(key == 'id') { series.id = val; }
			else {
				$.each(val, function(key,val) {
					var d = val.split(",");
					//Date needs to be converted to UTC for HighCharts...
					var x = Date.UTC(d[0], d[1], d[2]);
					seriesData.push([x, parseFloat(d[3])]);
				});
				series.data = seriesData;
			}
		});
		allSeries.push(series);
	});
	return allSeries;
}


function drawNavigator(data) {
	allSeries = createNavigatorSeries(data);
	// Create the chart
	new Highcharts.StockChart({
		chart : {
			renderTo : 'platform_pageview_chart',
			height: 120,
		},
		navigator: { height: 55 },
		exporting: { enabled: false },
		rangeSelector : { enabled: true, selected: 0 },
		title : { enabled: false },
		yAxis: {
			height: 0,
			gridLineWidth: 0,
			labels: { enabled: true }
		},
		// Note: The navigator does not show tooltip by default. 
		// An addin can be used: http://www.highcharts.com/plugin-registry/single/44/Navigator%20tooltips
		// tooltip: { enabled: true, valueDecimals: 2 },
		// tooltip: {
		// 	enabled: true, 
		// 	crosshairs: [true, true]
		// },
		series: allSeries,
		xAxis: {
			lineWidth: 0,
			tickLength : 0,
			labels: { enabled: false },
			events: {
				// Navigator range changed event handler
				afterSetExtremes: function (e) {
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
				}// End of afterSetExtremes: function (e) {
			}
		}// End of xAxis: {
	});
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
			var dispName = getObjectDisplayName(chart["objectDisplayNames"], seriesName);
			var newData = {
				name: dispName,
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
			data: dataset,
			point:{
				events:{
					click: function (event) {
					// mouseOver: function (event) {
						// alert(this.x + " " + this.y);
						console.log(this);
						console.log(event);
						testDrawHalfPie();
					}
				}
			}  
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

	// if(chart["detailChart"]) {
	// 	chart["detailChart"]["series"] = createPieChartSeries(chart["detailChart"], true, checkDate, start, end, colors);
	// }
	if(chart["objValues"]) {
		chart["detailChart"]["series"] = testCreatePieChartSeries(chart["objValues"], true, checkDate, start, end, colors);
	}
	
	return allSeries;
}


function testCreatePieChartSeries(chart, isDetailChart, checkDate, start, end, colors) {
	var allSeries = [];
	if (colors == null || colors.length == 0) {
		colors = createChartColors(chart["seriesName"]);
	}

	var posX = PIE_INIT_POSITION_X;
	$.each(chart["data"], function(key, val) {
		dataset = [];
		if (parseInt(key) > 0) {
			posX += PIE_OFFSET;
		}
		$.each(val["series"], function(key, dataSeries) {
			var index = 0;
			$.each(dataSeries["date"], function(key, date) {
				canAdd = true;
				if(checkDate) {
					var d = date.split(",");
                    var utcDate = Date.UTC(d[0], d[1], d[2]);
					if( !(parseFloat(start) <= parseFloat(utcDate) && parseFloat(end) >= parseFloat(utcDate)) ) {
						canAdd = false
					}
				}
				if (!canAdd) return true;

				var dispName = getObjectDisplayName(chart["objectDisplayNames"], dataSeries["name"]);
				dispName = dispName + " (" + date + ")" + "<br>" + dataSeries["values"][index++];
				var newData = {
					name: dispName,
					y: 1
				};
				if(!isDetailChart) {
					newData["color"] = getChartColorByName(colors, dataSeries["name"], true);
				}
				else if(isDetailChart && val["series"].length > 0) {
					// Color of each piece of outer pie is similar to that of collesponding inner piece
					var verb = null;
					$.each(chart["objectMapper"], function(key, element) {
						if ($.inArray(dataSeries["name"], element) != -1) {
							verb = key;
							return true;
						}
					});
					newData["color"] = getChartColorByName(colors, verb, false);
					dataset.push(newData);
				}
			});
		});

		colorIndex = 0;
		diameter = isDetailChart ? PIE_DIAMETER_OUTER : PIE_DIAMETER_INNER;
		var newSeries = {
			type: chart['type'],
			name: val["category"],
			center: [posX, null],
			size: diameter,
			dataLabels:{
				formatter: function () {
					// return this.y > 0 ? '<b>' + this.point.name + '</b>' : null;
					// return this.y > 0 ? this.point.name : null;
					return null;
				},
				distance: -20
			},
			data: dataset
		}
		if(isDetailChart) {
			newSeries["innerSize"] = PIE_DIAMETER_INNER;
			newSeries["dataLabels"] = {
				formatter: function () {
					// return this.y > 0 ? '<b>' + this.point.name + ': ' + this.y + '</b>' : null;
					return null;
				},
				distance: -5
				// enable: false
			};
		}
		allSeries.push(newSeries);
	});

	return allSeries;
}


function getObjectDisplayName(displayNames, objectName) {
	if(displayNames == null || objectName == null) {
		return objectName;
	}

	var ret = objectName;
	try {
		$.each(displayNames, function(key, val) {
			if(key == objectName) {
				ret = val;
				return true;
			}
		});
	} catch(e) {
		console.log("An exception has occurred in getObjectDisplayName() method.");
		console.log(e);
	}
	return ret;
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
	// Add Initial position X and subtract a little bit to adjust the width
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
			text: chart["title"],
            align: 'center',
            verticalAlign: 'top'
		},
        labels: {
            style: {
                // color: '#3E576F',
                fontSize: '20px'
            },
            items: labelItems
        },
        tooltip: {
        	style: {
                // color: '#3E576F',
                fontSize: '16px'
            },
            formatter: function() {
				format = //'<b>' + this.series.name + '</b><br>'
				// + '<b>' + this.point.name + ': ' + this.point.y + '</b>';
				'<b>' + this.point.name + '</b>';
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
		$.each(series, function(key, val) {
			$.each(val["data"], function(key, data) {
				if(dataSet[data["name"]]) {
					dataSet[data["name"]].push(data["y"]);
				} else {
					dataSet[data["name"]] = [data["y"]];
				}
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
		// Show graph area
		changeChartAreaVisibility(true, val);
		allPlatformData[val] = {};
		showCharts(val);
	});
	showPlatformTimeseries();
});
