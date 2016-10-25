// /**
//  * ccadashboard.js
//  * Authour: Koji Nishimoto
//  * Created: 22/10/2016
//  */
Common = function() {};
Common.inherit = function(childCtor, parentCtor) {
  /** @constructor */
  function tempCtor() {};
  tempCtor.prototype = parentCtor.prototype;
  childCtor.superClass_ = parentCtor.prototype;
  childCtor.prototype = new tempCtor();
  /** @override */
  childCtor.prototype.constructor = childCtor;
};

/**
 * CLAChart Constructor
 * @param {string} renderTo
 */
CLAChart = function(renderTo, chartType, url) {
	this.renderTo = renderTo;
	this.chartType = chartType;
	this.url = url;
	this.name = "CLAChart";
	// this.platforms = null; // All platforms
	this.selectedPlatform = null; // Platform name that user clicked on chart
	this.charts = []; // All data sent from the server
	this.series = []; // Current series
	this.categories = []; // Current categories
	this.dataType = CLAChart.DATA_TYPE_TOTAL // Current data type
};

CLAChart.DATA_TYPE_TOTAL = "total";
CLAChart.DATA_TYPE_OVERVIEW = "overview";
CLAChart.DATA_TYPE_DETAILS = "details";

/// 
/// These methods must be implemented in child object.
/// 
CLAChart.prototype.createSeries = function(data, checkDate, start, end) {
	if(data == null) return null;
	var charts = data["charts"];
	// Keep the data for later use
	this.charts = charts;
	// this.platforms = data["platforms"];
	this.series = this.createSeriesByChart(charts[CLAChart.DATA_TYPE_TOTAL], checkDate, start, end);
	this.categories = charts[CLAChart.DATA_TYPE_TOTAL]["categories"] ? charts[CLAChart.DATA_TYPE_TOTAL]["categories"] : [];
};
CLAChart.prototype.initializeChart = function(data) {		
	console.log(this.name + " chart type: ===> " + this.chartType);

	this.createSeries(data, false, null, null);
	this.changeChartAreaVisibility(this.renderTo, true);
	var options = this.createOptions();
	$("#" + this.renderTo).highcharts(options);
};
CLAChart.prototype.redraw = function(chart, dataType, checkDate, start, end) {
	throw new Error('Not Implemented');
};
CLAChart.prototype.draw = function() {
	var self = this;
	// console.log(this.url);
	$.ajax({
		type: "GET",
		url: this.url
	})
	.fail(function(data,textStatus, errorThrown){
		console.log('error!\r\n' + errorThrown);
	})
	.done(function( data ) {
		// console.log(" CLAChart");
		self.initializeChart(data);
	});
};
CLAChart.prototype.changeChartAreaVisibility = function(tagId, showChartArea) {
	if(showChartArea) {
		$("#" + tagId).show();
	} else {
		$("#" + tagId).hide();
	}
};
CLAChart.prototype.isValidDate = function(utcDate, start, end) {
	return parseFloat(start) <= parseFloat(utcDate) && parseFloat(end) >= parseFloat(utcDate);
};
CLAChart.prototype.countTotalActivities = function(series, checkDate, start, end, countable) {
	var total = 0;
	if(series == null || series.length == 0) return total;

	if(checkDate) {
		var index = 0;
		$.each(series["date"], function(key, value) {
			var d = value.split(",");
			var utcDate = Date.UTC(d[0], d[1], d[2]);
			// Add value when startDate <= value >= endDate
			// if(parseFloat(start) <= parseFloat(utcDate) && parseFloat(end) >= parseFloat(utcDate)) {
			if(this.isValidData(utcDate, start, end)) {
				if(countable) {
					total += series[0]["values"][index++];
				} else {
					// When the value is uncountable (str, etc.), increment total.
					total++;
				}
			}
		});
	} else {
		// Add up all values of the current series
		$.each(series["values"], function(key , value) {
			if(countable) {
				total += value;
			} else {
				// When the value is uncountable (str, etc.), increment total.
				total++;
			}
		});	
	}
	return total;
};
CLAChart.prototype.createChartColors = function(series) {
	var colors = Highcharts.getOptions().colors;
	if (series == null || series.length == 0) return colors;

	var colorIndex = 0;
	var ret = [];
	$.each(series, function(key, name) {
		obj = { name: name, color: colors[colorIndex % colors.length] };
		ret.push(obj);
		colorIndex++;
	});
	return ret;
};
CLAChart.prototype.getChartColorByName = function(colors, objectName, isBrighter) {
	var colorObj = colors.filter(function(item, index) {
		if (item["name"] == objectName) return true;
	});
	var ret = colorObj[0]["color"];
	if(isBrighter) {
		ret = Highcharts.Color(colorObj[0]["color"]).brighten(CLAPieChartOptions.CHART_COLOR_BRIGHTNESS).get();
	}
	return ret;
};
CLAChart.prototype.getParentObjectName = function(objectMapper, objectName) {
	var verb = objectName;
	if(objectMapper == null ) return verb;

	for(key in objectMapper) {
		if ($.inArray(objectName, objectMapper[key]) != -1) {
			verb = key;
			break;
			// return true;
		}
	}
	return verb;
};






CLANavigatorChart = function(renderTo, courseCode, platform, url) {
	CLAChart.call(this, renderTo, null, url);
	this.name = "CLANavigatorChart";
};
// Inherit CLAChart 
Common.inherit(CLANavigatorChart, CLAChart);

CLANavigatorChart.prototype.createSeries = function(data) {
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
};


/**
 * [initializeChart description]
 * @param  {[type]} data [description]
 * @return {[type]}      [description]
 */
CLANavigatorChart.prototype.initializeChart = function(data) {
	allSeries = this.createSeries(data);
	this.changeChartAreaVisibility(this.renderTo, true);
	var navOpt = new CLANavigatorChartOptions(this.renderTo, allSeries);
	new Highcharts.StockChart(navOpt.getOptions());
};




CLAPieChart = function(renderTo, chartType, courseCode, platform, url) {
	// var url = "/dashboard/api/get_platform_activities/?course_code=" + course_code + "&platform=" + platform;
	CLAChart.call(this, renderTo,chartType, url);
	this.name = "CLAPieChart";
};
Common.inherit(CLAPieChart, CLAChart);

CLAPieChart.prototype.createOptions = function() {
	var options = new CLAPieChartOptions(this.renderTo, this.chartType).getOptions();
	// Do not show anything on purpose in order to avoid overwrapping on category names
	options.title.text = " ";
	options.chart.width = CLAPieChartOptions.calculateChartAreaWidth(this.categories);
	options.labels.items = CLAPieChartOptions.getChartLabels(this.categories);
	options.series = this.series;
	options.plotOptions.series = this.getPointOptions(this.dataType);
	return options;
};
CLAPieChart.prototype.getPointOptions = function(dataType) {
	var self = this;
	var options = {
		point: {
			events: {
				click: function() {
					self.selectedPlatform = this.name;
					self.redrawByPoint(this); //this = point object
				}
			}
		}
	}
	return options;
};
CLAPieChart.prototype.redrawByPoint = function(point) {
	// console.log("Pie chart point was clicked: " 
	// 	+ point.name+":"+point.series.name+":"+point.y);
	var chart = null;
	var newDataType = CLAChart.DATA_TYPE_TOTAL;
	this.selectedPlatform = point.name;
	// When total data is currently shown in the chart, redraw (re-instanciate) chart with overview data
	if(this.dataType == CLAChart.DATA_TYPE_TOTAL) {
		chart = this.charts[this.selectedPlatform][CLAChart.DATA_TYPE_OVERVIEW];
		newDataType = CLAChart.DATA_TYPE_DETAILS; // Set details to draw double pie chart
	// } else if(this.dataType == CLAChart.DATA_TYPE_OVERVIEW) {
	// 	chart = this.charts[CLAChart.DATA_TYPE_TOTAL];
	// 	newDataType = CLAChart.DATA_TYPE_TOTAL;
	} else {
		chart = this.charts[CLAChart.DATA_TYPE_TOTAL];
		newDataType = CLAChart.DATA_TYPE_TOTAL;
	}

	this.redraw(chart, newDataType, false, null, null);
};

// CLAPieChart.prototype.redraw = function(chart, dataType, checkDate, start, end) {
// 	if(chart == null) return;
// 	this.series = this.createSeriesByChart(chart, checkDate, start, end);
// 	this.categories = chart["categories"] ? chart["categories"] : [];
// 	var options = this.createOptions();
// 	this.dataType = dataType;
// 	$("#" + this.renderTo).highcharts(options);
// };

CLAPieChart.prototype.getObjectDisplayName = function(objectMapper, objectName) {
	if(objectMapper == null || objectMapper.length == 0 || objectName == null) {
		return objectName;
	}

	var ret = objectName;
	try {
		$.each(objectMapper, function(key, val) {
			if(key == objectName) {
				ret = val;
				return false; // false means break in $.each()
			}
		});
	} catch(e) {
		console.log("An exception has occurred in getObjectDisplayName() method.");
		console.log(e);
	}
	return ret;
};

CLAPieChart.prototype.createSeriesByChart = function(chart, checkDate, start, end) {
	return this.createSeriesWithColors(chart, checkDate, start, end, null);
};
CLAPieChart.prototype.createSeriesWithColors = function(chart, checkDate, start, end, colors) {
	var allSeries = [];
	if (colors == null || colors.length == 0) {
		colors = this.createChartColors(chart["seriesName"]);
	}

	var posX = CLAPieChartOptions.PIE_INIT_POSITION_X;
	var seriesName = chart["seriesName"];
	var categories = chart["categories"];
	var countable = chart["countable"];
	var chartData = chart["data"];
	for(var i = 0; i < categories.length; i++) {
		if (i > 0) {
			posX += CLAPieChartOptions.PIE_OFFSET;
		}

		dataset = [];
		var cate = categories[i];
		var total = 0;
		for(var j = 0; j < seriesName.length; j++) {
			var name = seriesName[j];
			var series = chartData[cate][name];
			var total = this.countTotalActivities(series, checkDate, start, end, countable);
			var dispName = this.getObjectDisplayName(chart["objectMapper"], name);
			var newData = {
				name: dispName,
				y: total
			};
			var isBright = this.dataType == CLAChart.DATA_TYPE_TOTAL ? false : true;
			newData["color"] = this.getChartColorByName(colors, seriesName[j], isBright);
			dataset.push(newData);
		}
		var diameter = CLAPieChartOptions.PIE_DIAMETER_OUTER;
		if(this.dataType != CLAChart.DATA_TYPE_TOTAL) {
			// diameter = this.dataType == CLAChart.DATA_TYPE_DETAILS ? CLAPieChartOptions.PIE_DIAMETER_OUTER : CLAPieChartOptions.PIE_DIAMETER_INNER;
			diameter = CLAPieChartOptions.PIE_DIAMETER_INNER;
		}			
		newSeries = CLAPieChartOptions.getSeriesOptions(cate, posX, diameter, dataset);
		allSeries.push(newSeries);
	}
	if(this.dataType == CLAChart.DATA_TYPE_DETAILS) {
		var detailsSeries = this.createDetailsChartSeries(
							this.charts[this.selectedPlatform][CLAChart.DATA_TYPE_DETAILS],
							checkDate, start, end, colors);
		$.merge(allSeries, detailsSeries);
	}
	return allSeries;
};
CLAPieChart.prototype.createDetailsChartSeries = function(detailsChart, checkDate, start, end, colors) {
	var allSeries = [];
	if (colors == null || colors.length == 0) {
		colors = createChartColors(detailsChart["seriesName"]);
	}

	var posX = CLAPieChartOptions.PIE_INIT_POSITION_X;
	var seriesName = detailsChart["seriesName"];
	var categories = detailsChart["categories"];
	var chartData = detailsChart["data"];

	for(var i = 0; i < categories.length; i++) {
		dataset = [];
		if (i > 0) {
			posX += CLAPieChartOptions.PIE_OFFSET;
		}

		var cate = categories[i];
		for(var j = 0; j < seriesName.length; j++) {
			var name = seriesName[j];
			var series = chartData[cate][name];
			if(series == null) {
				continue;
			}
			var index = 0;
			for(var k = 0; k < series["date"].length; k++) {
				canAdd = true;
				var date = series["date"][k];
				if(checkDate) {
					var d = date.split(",");
                    var utcDate = Date.UTC(d[0], d[1], d[2]);
					if(this.isValidDate(utcDate, start, end)) {
						canAdd = false
					}
				}
				if (!canAdd) return true; // continue

				var dispName = this.getObjectDisplayName(detailsChart["objectDisplayNames"], series["name"]);
				dispName = dispName + " (" + date + ")" + "<br>" + series["values"][index++];
				var newData = {
					name: dispName,
					y: 1
				};
				var verb = this.getParentObjectName(detailsChart["objectMapper"], series["name"]);
				newData["color"] = this.getChartColorByName(colors, verb, false);
				dataset.push(newData);
			}
		}

		newSeries = CLAPieChartOptions.getSeriesOptions(cate, posX, CLAPieChartOptions.PIE_DIAMETER_OUTER, dataset);
		if(this.dataType == CLAChart.DATA_TYPE_DETAILS) {
			newSeries.innerSize = CLAPieChartOptions.PIE_DIAMETER_INNER;
			newSeries.dataLabels = {
				formatter: function () {
					return null;
				},
				distance: -5
			};
		}
		allSeries.push(newSeries);
	}

	return allSeries;
};




CLABarChart = function(renderTo, chartType, courseCode, platform, url) {
	// var url = "/dashboard/api/get_platform_activities/?course_code=" + course_code + "&platform=" + platform;
	CLAChart.call(this, renderTo, chartType, url);
	this.name = "CLABarChart";
};
// Inherit CLAChart
Common.inherit(CLABarChart, CLAChart);

CLABarChart.prototype.createSeriesByChart = function(chart, checkDate, start, end) {
	var allSeries = [];
	if(chart == null || chart["data"] == null || chart["data"].length == 0) {
		return allSeries;
	}
	var seriesName = chart["seriesName"];
	var categories = chart["categories"];
	var countable = chart["countable"];
	var chartData = chart["data"];
	var index = 0;
	for(var i = 0; i < seriesName.length; i++) {
		obj = [];
		name = seriesName[i];
		for(var j = 0; j < categories.length; j++) {
			cate = categories[j];
			series = chartData[cate][name];
			var total = this.countTotalActivities(series, checkDate, start, end, countable);
			obj.push(total);
		}
		var newSeries = {
			name: name,
			data: obj,
		};
		allSeries.push(newSeries);
		index++;
	}
	// this.series = allSeries;
	return allSeries;
};



CLABarChart.prototype.createOptions = function() {
	var options = new CLABarChartOptions(this.renderTo, this.chartType).getOptions();
	options.title.text = "Details of activities";
	options.yAxis.title.text = "Details of activities";
	options.xAxis.categories = this.categories;
	options.series = this.series;
	options.plotOptions.column.cursor = 'pointer';
	options.plotOptions.column.point = this.getPointOptions(this.dataType);
	return options;
};


CLABarChart.prototype.getPointOptions = function(dataType) {
	var self = this;
	var options = {
		events: {
			click: function () {
				self.selectedPlatform = this.series.name;
				self.redrawByPoint(this);
			}
		}
	}
	return options;
};
CLABarChart.prototype.redrawByPoint = function(point) {
	// console.log("bar chart point was clicked: " 
	// 	+ point.category+":"+point.series.name+":"+point.y);
	var chart = null;
	var newDataType = CLAChart.DATA_TYPE_TOTAL;
	// When total data is currently shown in the chart, redraw (re-instanciate) chart with overview data
	if(this.dataType == CLAChart.DATA_TYPE_TOTAL) {
		chart = this.charts[this.selectedPlatform][CLAChart.DATA_TYPE_OVERVIEW];
		newDataType = CLAChart.DATA_TYPE_OVERVIEW;
	// } else if(this.dataType == CLAChart.DATA_TYPE_OVERVIEW) {
	// 	chart = this.charts[CLAChart.DATA_TYPE_TOTAL];
	// 	newDataType = CLAChart.DATA_TYPE_TOTAL;
	} else {
		chart = this.charts[CLAChart.DATA_TYPE_TOTAL];
		newDataType = CLAChart.DATA_TYPE_TOTAL;
	}

	this.redraw(chart, newDataType, false, null, null);
};
CLAChart.prototype.initializeChart = function(data) {		
	// console.log(this.name + " chart type: ===> " + this.chartType);
	this.createSeries(data, false, null, null);
	this.changeChartAreaVisibility(this.renderTo, true);
	var options = this.createOptions();
	$("#" + this.renderTo).highcharts(options);
};
CLAChart.prototype.redraw = function(chart, dataType, checkDate, start, end) {
	if(chart == null) return;
	this.dataType = dataType;
	this.series = this.createSeriesByChart(chart, checkDate, start, end);
	this.categories = chart["categories"] ? chart["categories"] : [];
	var options = this.createOptions();
	$("#" + this.renderTo).highcharts(options);
};
// CLABarChart.prototype.redraw = function(chart, dataType, checkDate, start, end) {
// 	if(chart == null) return;
// 	this.series = this.createSeriesByChart(chart, checkDate, start, end);
// 	this.categories = chart["categories"] ? chart["categories"] : [];
// 	var options = this.createOptions();
// 	this.dataType = dataType;
// 	$("#" + this.renderTo).highcharts(options);
// };


CLAChartOptions = function(renderTo, chartType) {
	this.chartType = chartType;
	this.renderTo = renderTo;
	this.title = "";
	this.yAxisTitle = "";
	this.categories = [];
	this.series = [];
};
CLAChartOptions.prototype.getOptions = function () {
	throw Error("Not implemented");
};

CLANavigatorChartOptions = function(renderTo, series) {
	CLAChartOptions.call(this, renderTo, null);
	this.navigatorSeries = series;
};
Common.inherit(CLANavigatorChartOptions, CLAChartOptions);

CLANavigatorChartOptions.prototype.getOptions = function () {
	var options = {
		chart : {
			renderTo: this.renderTo,
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
		series: this.navigatorSeries,
		xAxis: {
			lineWidth: 0,
			tickLength : 0,
			labels: { enabled: false },
			// events: {
			// 	// Navigator range changed event handler
			// 	afterSetExtremes: function (e) {
			// 		if(allPlatformData != null) {
			// 			var platformNames = platform.split(",");
			// 			$.each(platformNames, function(key, val) {
			// 				chartData = createChartSeries(allPlatformData[val], true, e.min, e.max);
			// 				if(chartData != null) {
			// 					allPlatformData[val] = chartData;
			// 					drawGraphs(chartData);
			// 					showAllTables(chartData);
			// 				}
			// 			});
			// 		}
			// 	}// End of afterSetExtremes: function (e) {
			// }
		}// End of xAxis: {
	};
	return options;
};

CLABarChartOptions = function(renderTo, chartType) {
	if(chartType != CLABarChartOptions.CHART_TYPE_COLUMN && chartType != CLABarChartOptions.CHART_TYPE_BAR) {
		throw Error("Invalid chart type: " + chartType);
	}
	CLAChartOptions.call(this, renderTo, chartType);
};
/**
 * Chart type: column (Virtical bar chart)
 * @type {String}
 */
CLABarChartOptions.CHART_TYPE_COLUMN = "column";
/**
 * Chart type: bar (Horizontal bar chart)
 * @type {String}
 */
CLABarChartOptions.CHART_TYPE_BAR = "bar";

// Inherit CLAChartOptions
Common.inherit(CLABarChartOptions, CLAChartOptions);

CLABarChartOptions.prototype.getOptions = function () {
	var options = {
		chart: { type: this.chartType },
		title: { text: this.title },
		series: this.series,
		drilldown: this.drilldown,
		xAxis: { categories: this.categories },
		yAxis: {
			min: 0,
			allowDecimals: false,
			title: { text: this.yAxisTitle },
			stackLabels: {
				enabled: true,
				style: {
					fontWeight: 'bold',
					color: (Highcharts.theme && Highcharts.theme.textColor) || 'black'
				}
			}
		},
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
					style: { textShadow: '0 0 3px black' }
				},
				// cursor: 'pointer',
				// point: {
				// 	events: {
				// 		click: function () {
				// 			console.log("bar chart point was clicked: " 
				// 				+ this.category+":"+this.series.name+":"+this.y);
				// 			//$('#test').html(this.series);
				// 			//alert(this.name);
				// 		}
				// 	}
				// }
			}
		}
	}; // End of this.options
	return options;
};


CLAPieChartOptions = function(renderTo, chartType) {
	if(chartType != CLAPieChartOptions.CHART_TYPE_PIE) {
		throw Error("Invalid chart type: " + chartType);
	}
	CLAChartOptions.call(this, renderTo, chartType);
};
CLAPieChartOptions.CHART_TYPE_PIE = "pie";
CLAPieChartOptions.PIE_OFFSET = 410;
CLAPieChartOptions.PIE_INIT_POSITION_X = 140;
CLAPieChartOptions.PIE_DIAMETER_INNER = 140;
CLAPieChartOptions.PIE_DIAMETER_OUTER = 270;
CLAPieChartOptions.CHART_COLOR_BRIGHTNESS = 0.2;
// Inherit CLAChartOptions
Common.inherit(CLAPieChartOptions, CLAChartOptions);

CLAPieChartOptions.prototype.getOptions = function() {
	var options = {
		chart: {
			type: this.chartType,
			width: $("#" + this.renderTo).width()
		},
		title: {
			text: this.title,
			align: 'center',
			verticalAlign: 'top'
		},
		labels: { 
			style: { fontSize: '20px' },
			items: []//labelItems
		},
		tooltip: {
			style: { fontSize: '16px' },
			formatter: function() {
				format = //'<b>' + this.series.name + '</b><br>'
				"<b>" + this.point.name + "</b>";
				// '<b>' + this.point.name + '</b>';
				return format;
			}
		},
		plotOptions: {
			pie: { cursor: 'pointer' }
		},
		series: []
	}; // End of this.options
	return options;
};

CLAPieChartOptions.getSeriesOptions = function (category, posX, diameter, dataset) {
	// var chartWidth = calculateChartAreaWidth(chart);
	// var labelItems = getChartLabels(chart["categories"]);
	colorIndex = 0;
	// diameter = isDetailChart ? PIE_DIAMETER_OUTER : PIE_DIAMETER_INNER;
	var options = {
		type: this.chartType,
		name: category,
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
	};
	return options;
};
CLAPieChartOptions.getChartLabels = function(categories) {
	var items = [];
	var left = CLAPieChartOptions.PIE_INIT_POSITION_X - 30;
	var index = 0;
	$.each(categories, function(key, cate) {
		if(key > 0) {
			left += CLAPieChartOptions.PIE_OFFSET;
		}
		label = {
			html: cate,
			style: { left: left, top: 10 }
		}
		items.push(label);
	});
	return items;
};

CLAPieChartOptions.calculateChartAreaWidth = function(categories) {
	// Pie size * num of categories
	var areaWidth = (categories.length * CLAPieChartOptions.PIE_DIAMETER_OUTER);
	// Add offset width between pies
	areaWidth += (categories.length - 1) * (CLAPieChartOptions.PIE_OFFSET - CLAPieChartOptions.PIE_DIAMETER_OUTER);
	// Add Initial position X and subtract a little bit to adjust the width
	areaWidth += CLAPieChartOptions.PIE_INIT_POSITION_X - 30;
	return areaWidth
};


$(document).ready(function(){
	// Draw the navigator
	var url = "/dashboard/api/get_platform_timeseries_data/?course_code=" + course_code + "&platform=" + platform;
	var navChart = new CLANavigatorChart("chartNavigator", "PROJ-TEAM2", "Trello", url);
	navChart.changeChartAreaVisibility("activities", true);
	navChart.draw();

	url = "/dashboard/api/get_platform_activities/?course_code=" + course_code + "&platform=" + platform;
	var barChart = new CLABarChart("activityColumn", CLABarChartOptions.CHART_TYPE_COLUMN, "PROJ-TEAM2", "Trello", url);
	barChart.draw();
	var pieChart = new CLAPieChart("activityPie", CLAPieChartOptions.CHART_TYPE_PIE, "PROJ-TEAM2", "Trello", url);
	pieChart.draw();
	
});


// /**
//  * Inner pie chart diameter
//  * It is used for a donut pie chart.
//  * @type {Number}
//  */
// var PIE_DIAMETER_INNER = 140;

// /**
//  * Outer pie chart diameter
//  * It is used for a single pie chart.
//  * @type {Number}
//  */
// var PIE_DIAMETER_OUTER = 270;

// /**
//  * First pie chart's position X
//  * @type {Number}
//  */
// var PIE_INIT_POSITION_X = 140;

// /**
//  * Distance between next pie chart
//  * @type {Number}
//  */
// var PIE_OFFSET = 410;

// /**
//  * Brightness of chart color
//  * @type {Number}
//  */
// var CHART_COLOR_BRIGHTNESS = 0.2;

// /**
//  * Show platform timeseries chart
//  */
// function showPlatformTimeseries() {
// 	$.ajax({
//  		type: "GET",
// 		url: "/dashboard/api/get_platform_timeseries_data/?course_code=" + course_code + "&platform=" + platform
// 	})
// 	.fail(function(data,textStatus, errorThrown){
//     	console.log('error!\r\n' + errorThrown);
// 	})
// 	.done(function( data ) {
// 		drawNavigator(data);
// 	});// End of .done(function( data ) {
// }


// function createNavigatorSeries(data) {
// 	allSeries = [];
// 	$.each(data["series"], function(key,value) {
// 		var series = { 
// 			name : '',
// 			lineWidth: 0,
// 			marker: {
// 				enabled: false,
// 				states: {
// 					hover: { enabled: false }
// 				}
// 			},
// 			data : [],
// 		};

// 		var seriesData = [];
// 		$.each(value, function(key,val) {
// 			if (key == 'name')   { series.name = val; }
// 			else if(key == 'id') { series.id = val; }
// 			else {
// 				$.each(val, function(key,val) {
// 					var d = val.split(",");
// 					//Date needs to be converted to UTC for HighCharts...
// 					var x = Date.UTC(d[0], d[1], d[2]);
// 					seriesData.push([x, parseFloat(d[3])]);
// 				});
// 				series.data = seriesData;
// 			}
// 		});
// 		allSeries.push(series);
// 	});
// 	return allSeries;
// }


// // function drawNavigator(data) {
// // 	allSeries = createNavigatorSeries(data);
// // 	// Create the chart
// // 	new Highcharts.StockChart({
// // 		chart : {
// // 			renderTo : 'platform_pageview_chart',
// // 			height: 120,
// // 		},
// // 		navigator: { height: 55 },
// // 		exporting: { enabled: false },
// // 		rangeSelector : { enabled: true, selected: 0 },
// // 		title : { enabled: false },
// // 		yAxis: {
// // 			height: 0,
// // 			gridLineWidth: 0,
// // 			labels: { enabled: true }
// // 		},
// // 		// Note: The navigator does not show tooltip by default. 
// // 		// An addin can be used: http://www.highcharts.com/plugin-registry/single/44/Navigator%20tooltips
// // 		// tooltip: { enabled: true, valueDecimals: 2 },
// // 		// tooltip: {
// // 		// 	enabled: true, 
// // 		// 	crosshairs: [true, true]
// // 		// },
// // 		series: allSeries,
// // 		xAxis: {
// // 			lineWidth: 0,
// // 			tickLength : 0,
// // 			labels: { enabled: false },
// // 			events: {
// // 				// Navigator range changed event handler
// // 				afterSetExtremes: function (e) {
// // 					if(allPlatformData != null) {
// // 						var platformNames = platform.split(",");
// // 						$.each(platformNames, function(key, val) {
// // 							chartData = createChartSeries(allPlatformData[val], true, e.min, e.max);
// // 							if(chartData != null) {
// // 								allPlatformData[val] = chartData;
// // 								drawGraphs(chartData);
// // 								showAllTables(chartData);
// // 							}
// // 						});
// // 					}
// // 				}// End of afterSetExtremes: function (e) {
// // 			}
// // 		}// End of xAxis: {
// // 	});
// // }

// /**
//  * Show a chart and a table.
//  * Data is retrieved from the web server.
//  * 
//  * @param {String} platform Platform name
//  */
// function showCharts(platform) {
// 	if(platform == undefined || platform == "None" || platform == "" || platform.length == 0) {
// 		showMessage('Error: No platforms found. Charts and tables could not be generated.');
// 		return;
// 	}
// 	$.ajax({
// 		url: "/dashboard/api/get_platform_activities/?course_code=" + course_code + "&platform=" + platform
// 	})
// 	.fail(function(data, textStatus, errorThrown){
//     	console.log('Error has occurred in showCharts() function. PlatformName: ' + platform + ".\r\n" + errorThrown);
// 	})
// 	.done(function( data ) {
// 		chartData = createChartSeries(data, false, null, null)
// 		allPlatformData[platform] = chartData;
// 		drawGraphs(chartData);
// 		showAllTables(chartData);
// 		// allPlatformData = chartData;
// 	});
// }

// /**
//  * Create series for charts.
//  * Sample series that will be created is shown below. (for bar chart)
// 	"series": [{
// 			"name": "created", 
// 			"data":[1,2,6,2,4,5,2,6,8,3]
// 		}, {
// 			"name": "updated", 
// 			"data": [2,0,4,5,9,7,2,3,5,6]
// 	}]
//  * @param  {[Object]} data JSON data for charts
//  * @param  {[boolean]} checkDate if true, data between start date and end date that user selected in the navigator 
//  *                               at the Platform Timeseries, will be returned.
//  */
// function createChartSeries(data, checkDate, start, end) {
// 	if(data == null) {
// 		return null;
// 	}


// 	$.each(data["results"], function(key, result) {
// 		$.each(result["platforms"], function(key, chart) {

// 			var allSeries = null;
// 			switch(chart['type']) {
// 				case 'column':
// 					chart["series"] = createBarChartSeries(chart, checkDate, start, end);
// 					break;
// 				case 'pie':
// 					chart["series"] = createPieChartSeries(chart, false, checkDate, start, end);
// 					break;
// 				default:
// 					break;
// 			}
// 		});
// 	});
// 	return data;

// 	// $.each(data, function(key, val) {
// 	// 	$.each(val["charts"], function(key, chart) {
// 	// 		var allSeries = null;
// 	// 		switch(chart['type']) {
// 	// 			case 'column':
// 	// 				chart["series"] = createBarChartSeries(chart, checkDate, start, end);
// 	// 				break;
// 	// 			case 'pie':
// 	// 				chart["series"] = createPieChartSeries(chart, false, checkDate, start, end);
// 	// 				break;
// 	// 			default:
// 	// 				break;
// 	// 		}
// 	// 	});
// 	// });
// 	// return data;
// }


// function createPieChartSeries(chart, isDetailChart, checkDate, start, end, colors) {
// 	var allSeries = [];
// 	if (colors == null || colors.length == 0) {
// 		colors = createChartColors(chart["seriesName"]);
// 	}

// 	posX = PIE_INIT_POSITION_X;
// 	$.each(chart["categories"], function(key, cate) {
// 		if (parseInt(key) > 0) {
// 			posX += PIE_OFFSET;
// 		}

// 		dataset = [];
// 		$.each(chart["seriesName"], function(key, seriesName) {
// 			var userData = chart["data"].filter(function(item, index){
// 			  if (item["category"] == cate) return true;
// 			});
// 			var series = userData[0]["series"].filter(function(item, index) {
// 				if (item["name"] == seriesName) return true;
// 			});

// 			var total = 0;
// 			if(series.length > 0) {
// 				if(checkDate) {
// 					$.each(series[0]["date"], function(key, value) {
// 	                    var d = value.split(",");
// 	                    var utcDate = Date.UTC(d[0], d[1], d[2]);
// 						// Add value when startDate <= value >= endDate
// 						if(parseFloat(start) <= parseFloat(utcDate) && parseFloat(end) >= parseFloat(utcDate)) {
// 							total += series[0]["values"][key];
// 						}
// 					});
// 				} else {
// 					// Add up all values of the current series
// 					$.each(series[0]["values"], function(key , value) {
// 						total += value;
// 					});
// 				}
// 			}
// 			var dispName = getObjectDisplayName(chart["objectDisplayNames"], seriesName);
// 			var newData = {
// 				name: dispName,
// 				y: total
// 			};
// 			if(!isDetailChart) {
// 				newData["color"] = getChartColorByName(colors, seriesName, true);
// 			}
// 			else if(isDetailChart && series.length > 0) {
// 				// Color of each piece of outer pie is similar to that of collesponding inner piece
// 				var verb = null;
// 				$.each(chart["objectMapper"], function(key, element) {
// 					if ($.inArray(seriesName, element) != -1) {
// 						verb = key;
// 						return true;
// 					}
// 				});

// 				newData["color"] = getChartColorByName(colors, verb, false);
// 			}
// 			dataset.push(newData);
// 		});
// 		colorIndex = 0;
// 		diameter = isDetailChart ? PIE_DIAMETER_OUTER : PIE_DIAMETER_INNER;
// 		var newSeries = {
// 			type: chart['type'],
// 			name: cate,
// 			center: [posX, null],
// 			size: diameter,
// 			// dataLabels: {enabled: false},
// 			dataLabels:{
// 				formatter: function () {
// 					// return this.y > 0 ? '<b>' + this.point.name + '</b>' : null;
// 					return this.y > 0 ? this.point.name : null;
// 				},
// 				distance: -20
// 			},
// 			data: dataset,
// 			point:{
// 				events:{
// 					click: function (event) {
// 					// mouseOver: function (event) {
// 						// alert(this.x + " " + this.y);
// 						console.log(this);
// 						console.log(event);
// 						testDrawHalfPie();
// 					}
// 				}
// 			}  
// 		}
// 		if(isDetailChart) {
// 			// newSeries["size"] = PIE_DIAMETER_OUTER;
// 			newSeries["innerSize"] = PIE_DIAMETER_INNER;
// 			newSeries["dataLabels"] = {
// 				formatter: function () {
// 					return this.y > 0 ? '<b>' + this.point.name + ': ' + this.y + '</b>' : null;
// 				},
// 				distance: -5
// 			};
// 		}
// 		allSeries.push(newSeries);
// 	});

// 	if(chart["detailChart"]) {
// 		chart["detailChart"]["series"] = testCreatePieChartSeries(chart["detailChart"], true, checkDate, start, end, colors);
// 	}
	
// 	return allSeries;
// }


// function testCreatePieChartSeries(chart, isDetailChart, checkDate, start, end, colors) {
// 	var allSeries = [];
// 	if (colors == null || colors.length == 0) {
// 		colors = createChartColors(chart["seriesName"]);
// 	}

// 	var posX = PIE_INIT_POSITION_X;
// 	$.each(chart["data"], function(key, val) {
// 		dataset = [];
// 		if (parseInt(key) > 0) {
// 			posX += PIE_OFFSET;
// 		}
// 		$.each(val["series"], function(key, dataSeries) {
// 			var index = 0;
// 			$.each(dataSeries["date"], function(key, date) {
// 				canAdd = true;
// 				if(checkDate) {
// 					var d = date.split(",");
//                     var utcDate = Date.UTC(d[0], d[1], d[2]);
// 					if( !(parseFloat(start) <= parseFloat(utcDate) && parseFloat(end) >= parseFloat(utcDate)) ) {
// 						canAdd = false
// 					}
// 				}
// 				if (!canAdd) return true;

// 				var dispName = getObjectDisplayName(chart["objectDisplayNames"], dataSeries["name"]);
// 				dispName = dispName + " (" + date + ")" + "<br>" + dataSeries["values"][index++];
// 				var newData = {
// 					name: dispName,
// 					y: 1
// 				};
// 				if(!isDetailChart) {
// 					newData["color"] = getChartColorByName(colors, dataSeries["name"], true);
// 				}
// 				else if(isDetailChart && val["series"].length > 0) {
// 					// Color of each piece of outer pie is similar to that of collesponding inner piece
// 					var verb = null;
// 					$.each(chart["objectMapper"], function(key, element) {
// 						if ($.inArray(dataSeries["name"], element) != -1) {
// 							verb = key;
// 							return true;
// 						}
// 					});
// 					newData["color"] = getChartColorByName(colors, verb, false);
// 					dataset.push(newData);
// 				}
// 			});
// 		});

// 		colorIndex = 0;
// 		diameter = isDetailChart ? PIE_DIAMETER_OUTER : PIE_DIAMETER_INNER;
// 		var newSeries = {
// 			type: chart['type'],
// 			name: val["category"],
// 			center: [posX, null],
// 			size: diameter,
// 			dataLabels:{
// 				formatter: function () {
// 					// return this.y > 0 ? '<b>' + this.point.name + '</b>' : null;
// 					// return this.y > 0 ? this.point.name : null;
// 					return null;
// 				},
// 				distance: -20
// 			},
// 			data: dataset
// 		}
// 		if(isDetailChart) {
// 			newSeries["innerSize"] = PIE_DIAMETER_INNER;
// 			newSeries["dataLabels"] = {
// 				formatter: function () {
// 					// return this.y > 0 ? '<b>' + this.point.name + ': ' + this.y + '</b>' : null;
// 					return null;
// 				},
// 				distance: -5
// 				// enable: false
// 			};
// 		}
// 		allSeries.push(newSeries);
// 	});

// 	return allSeries;
// }


// function getObjectDisplayName(displayNames, objectName) {
// 	if(displayNames == null || objectName == null) {
// 		return objectName;
// 	}

// 	var ret = objectName;
// 	try {
// 		$.each(displayNames, function(key, val) {
// 			if(key == objectName) {
// 				ret = val;
// 				return true;
// 			}
// 		});
// 	} catch(e) {
// 		console.log("An exception has occurred in getObjectDisplayName() method.");
// 		console.log(e);
// 	}
// 	return ret;
// }


// function getChartColorByName(colors, seriesName, isBrighter) {
// 	var series = colors.filter(function(item, index) {
// 		if (item["name"] == seriesName) return true;
// 	});
// 	// return Highcharts.Color(series[0]["color"]).brighten(0.4).get();
// 	color = series[0]["color"];
// 	if(isBrighter) {
// 		color = Highcharts.Color(series[0]["color"]).brighten(CHART_COLOR_BRIGHTNESS).get();
// 	}
// 	return color;
// }


// function createChartColors(series) {
// 	var colors = Highcharts.getOptions().colors;
// 	var colorIndex = 0;
// 	var ret = [];
// 	$.each(series, function(key, name) {
// 		obj = { name: name, color: colors[colorIndex % colors.length] };
// 		ret.push(obj);
// 		colorIndex++;
// 	});
// 	return ret;
// }


// function createBarChartSeries(chart, checkDate, start, end) {
// 	var allSeries = [];
// 	$.each(chart["seriesName"], function(key, seriesName) {
// 		obj = [];
// 		$.each(chart["categories"], function(key, cate) {
// 			// Search current category (user name, etc.) and series (verb, etc.) in chart["data"]
// 			var userData = chart["data"].filter(function(item, index){
// 			  if (item["category"] == cate) return true;
// 			});
// 			var series = userData[0]["series"].filter(function(item, index) {
// 				if (item["name"] == seriesName) return true;
// 			});

// 			var total = 0;
// 			if(series.length > 0) {
// 				if(checkDate) {
// 					$.each(series[0]["date"], function(key, value) {
// 	                    var d = value.split(",");
// 	                    var utcDate = Date.UTC(d[0], d[1], d[2]);
// 						// Add value when startDate <= value >= endDate
// 						if(parseFloat(start) <= parseFloat(utcDate) && parseFloat(end) >= parseFloat(utcDate)) {
// 							total += series[0]["values"][key];
// 						}
// 					});
// 				} else {
// 					// Add up all values of the current series
// 					$.each(series[0]["values"], function(key , value) {
// 						total += value;
// 					});	
// 				}
// 			}
// 			obj.push(total);
// 		});
// 		var newSeries = {
// 			name: seriesName,
// 			data: obj
// 		};
// 		allSeries.push(newSeries);
// 	});

// 	return allSeries;
// }

// /**
//  * Draw all .
//  * 
//  * @param {Object} data 	Chart data
//  */
// function drawGraphs(data) {
// 	$.each(data, function(key , val) {
// 		$.each(val["charts"], function(key , chart) {
// 			if ($('#' + chart['type'] + '-' + key).highcharts()) {
// 				$('#' + chart['type'] + '-' + key).highcharts().destroy();
// 			}
// 			switch(chart['type']) {
// 				case 'column':
// 					drawBarChart(chart, val["platform"]);
// 					break;
// 				case 'pie':
// 					// Draw single/inner pie chart
// 					// Note that outer pie has not been drawn yet
// 					drawPieChart(chart, val["platform"]);
// 					if(chart["detailChart"]) {
// 						$.each(chart["detailChart"]["series"], function(key, series) {
// 							// To draw outer pie, add outer pie series to chart
// 							addSeriesToChart(series, chart['type'], val["platform"]);
// 						});
// 					}
// 					break;
// 				default:
// 					break;
// 			}
// 		});
// 	});
// }

// function changeChartAreaVisibility(showChartArea, platform) {
// 	if(showChartArea) {
// 		$("#chartRoot-" + platform).show();
// 	} else {
// 		$("#chartRoot-" + platform).hide();
// 	}
// }

// function addSeriesToChart(series, chartType, platform) {
// 	var chart = $('#' + chartType + '-' + platform).highcharts();
// 	chart.addSeries(series);
// }

// function calculateChartAreaWidth(chart) {
// 	// Pie size * num of categories
// 	var areaWidth = (chart["categories"].length * PIE_DIAMETER_OUTER);
// 	// Add offset width between pies
// 	areaWidth += (chart["categories"].length - 1) * (PIE_OFFSET - PIE_DIAMETER_OUTER);
// 	// Add Initial position X and subtract a little bit to adjust the width
// 	areaWidth += PIE_INIT_POSITION_X - 30;
// 	return areaWidth
// }


// function getChartLabels(categories) {
// 	var items = [];
// 	var left = PIE_INIT_POSITION_X - 30;
// 	var index = 0;
// 	$.each(categories, function(key, cate) {
// 		if(key > 0) {
// 			left += PIE_OFFSET;
// 		}
// 		label = {
// 			html: cate,
// 			style: { left: left, top: 10 }
// 		}
// 		items.push(label);
// 	});
// 	return items;
// }


// /**
//  * Draw pie chart.
//  * @param  {[type]} chart [description]
//  * @return {[type]}       [description]
//  */
// function drawPieChart(chart, platform) {
// 	chartWidth = calculateChartAreaWidth(chart);
// 	labelItems = getChartLabels(chart["categories"]);
// 	$('#' + chart['type'] + '-' + platform).highcharts({
// 		chart: {
// 			type: chart["type"],
//             // width: parseInt($('#column-' + platform).width()) > 900 ? parseInt($('#column-' + platform).width()) : 900
//             width: chartWidth
// 		},
// 		title: {
// 			text: chart["title"],
//             align: 'center',
//             verticalAlign: 'top'
// 		},
//         labels: {
//             style: {
//                 // color: '#3E576F',
//                 fontSize: '20px'
//             },
//             items: labelItems
//         },
//         tooltip: {
//         	style: {
//                 // color: '#3E576F',
//                 fontSize: '16px'
//             },
//             formatter: function() {
// 				format = //'<b>' + this.series.name + '</b><br>'
// 				// + '<b>' + this.point.name + ': ' + this.point.y + '</b>';
// 				'<b>' + this.point.name + '</b>';
// 				return format;
//             }
//         },
//         plotOptions: {
//             pie: {
//                 // allowPointSelect: true,
//                 cursor: 'pointer'
//             }
//         },
//         series: chart["series"]
// 	});
// }

// /**
//  * Draw bar chart.
//  * @param  {[type]} chart [description]
//  * @return {[type]}       [description]
//  */
// function drawBarChart(chart, platform) {
// 	$('#' + chart['type'] + '-' + platform).highcharts({
// 		chart: {
// 			type: chart["type"]
// 		},
// 		title: {
// 			text: chart["title"]
// 		},
// 		yAxis: {
// 			min: 0,
// 			allowDecimals: false,
// 			title: {
// 			    text: chart['yAxis']["title"]
// 			},
//             stackLabels: {
//                 enabled: true,
//                 style: {
//                     fontWeight: 'bold',
//                     color: (Highcharts.theme && Highcharts.theme.textColor) || 'black'
//                 }
//             }
// 		},
// 		xAxis: {
// 			categories: chart["categories"]
// 		},

//         series: chart["series"],
//         tooltip: {
//             headerFormat: '<b>{point.x}</b><br/>',
//             pointFormat: '{series.name}: {point.y}<br/>Total: {point.stackTotal}'
//         },
//         plotOptions: {
//             column: {
//                 stacking: 'normal',
//                 dataLabels: {
//                     enabled: true,
//                     color: (Highcharts.theme && Highcharts.theme.dataLabelsColor) || 'white',
//                     style: {
//                         textShadow: '0 0 3px black'
//                     }
//                 }
//             }
//         }
// 	});
// }


// /**
//  * Show all tables in CCA dashboard.
//  * 
//  * @param {Object} data 	Chart data
//  */
// function showAllTables(data) {
// 	$.each(data, function(key , val) {
// 		$.each(val["charts"], function(key , chart) {
// 			showTable(chart, key);
// 			// Show table of details chart (outer pie, drilldown bar, etc.)
// 			// showTable(chart["detailChart"], val["platform"]);
// 		});
// 	});
// }

// function showTable(chart, platform) {
// 	if (chart == null) return;
// 	// In $.each(), keyword "continue" does not work. 
// 	// Return anything that's not false and it will behave as a continue. 
// 	// Return false, and it will behave as a break:
// 	if(parseInt(chart["showTable"]) != 1) return true;

// 	//TODO: Code needs to be modified for other type of charts 
// 	//Create data columns
// 	var cate = chart["categories"];
// 	var cols = [];
// 	var ary = {"title": ""};
// 	cols.push(ary);
// 	$.each(cate, function(key, val) {
// 		ary = {"title": val};
// 		cols.push(ary);
// 	});

// 	//Create table data
// 	newData = getTableData(chart);
// 	var elemName = chart["type"] + "-" + platform;
// 	if ($('#datatable-' + elemName).dataTable.isDataTable()) {
// 		$('#datatable-' + elemName).dataTable.fnDestroy();
// 	}
// 	$('#datatable-' + elemName).DataTable( {
// 		bFilter: false,
// 		bInfo: false,
// 		bPaginate: false,
// 		bLengthChange: false,
// 		bDestroy: true, //To reinitialise datatable, this has to be true.
// 		bSort: false,
// 		scrollX: true,
// 		// scrollY: 200, //maximum hight of the table
// 		data: newData,
// 		columns: cols
// 	});
// }


// function getTableData(chart) {
// 	var series = chart["series"];
// 	var newData = [];
// 	ary = [];
// 	if(chart["type"] == "pie") {
// 		var dataSet = {}
// 		$.each(series, function(key, val) {
// 			$.each(val["data"], function(key, data) {
// 				if(dataSet[data["name"]]) {
// 					dataSet[data["name"]].push(data["y"]);
// 				} else {
// 					dataSet[data["name"]] = [data["y"]];
// 				}
// 			});
// 		});

// 		$.each(dataSet, function(key, val) {
// 			ary.push(key);
// 			$.merge(ary, val)
// 			newData.push(ary);
// 			ary = [];
// 		});
// 	} else {
// 		$.each(series, function(key, val) {
// 			ary.push(val["name"]);
// 			$.merge(ary, val["data"])
// 			newData.push(ary);
// 			ary = [];
// 		});
// 	}
// 	return newData;
// }


// /**
//  * Show message.
//  * @param  {[String]} message Message to show.
//  */
// function showMessage(message) {
// 	$("#message").append(message);
// 	$("#message").show();
// }

// /**
//  * Load function.
//  */
// $(document).ready(function(){
// 	//Show charts and tables
// 	var platformNames = platform.split(",");
// 	$.each(platformNames, function(key, val) {
// 		// Show graph area
// 		changeChartAreaVisibility(true, val);
// 		allPlatformData[val] = {};
// 		showCharts(val);
// 	});
// 	showPlatformTimeseries();
// });
