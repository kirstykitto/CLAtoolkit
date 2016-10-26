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
CLAChart.saveChartObject = function(objInstance) {
	chartObjDict[objInstance.renderTo] = objInstance;
};

CLAChart.prototype.createSeries = function(data, checkDate, start, end) {
	if(data == null) return null;
	var charts = data["charts"];
	// Keep the data for later use
	this.charts = charts;
	this.series = this.createSeriesByChart(charts[CLAChart.DATA_TYPE_TOTAL], checkDate, start, end);
	this.categories = charts[CLAChart.DATA_TYPE_TOTAL]["categories"] ? charts[CLAChart.DATA_TYPE_TOTAL]["categories"] : [];
};
CLAChart.prototype.initializeChart = function(data) {		
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
	var self = this;
	if(checkDate) {
		for(var i = 0; i < series["date"].length; i++) {
			var d = series["date"][i].split(",");
			var utcDate = Date.UTC(d[0], d[1], d[2]);
			// Add value when startDate <= value >= endDate
			if(self.isValidDate(utcDate, start, end)) {
				if(countable) {
					total += series["values"][i];
				} else {
					// When the value is uncountable (str, etc.), increment total.
					total++;
				}
			}
		}
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
	var navOpt = new CLANavigatorChartOptions(this.renderTo, allSeries).getOptions();
	navOpt.series = allSeries;
	//Note: StockChart() method needs to be called instead of calling Chart()
	new Highcharts.StockChart(navOpt, function (chart) {
		// This code is for showing multiple series in the navigator
		// Note that afterSetExtremes() method will be called as chart.addSeries() method is called.
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
};




CLAPieChart = function(renderTo, chartType, courseCode, platform, url) {
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
					self.redrawByPoint(this, startDate, endDate); //this = point object
				}
			}
		}
	}
	return options;
};
CLAChart.prototype.getChartData = function(platform, dataType) {
	var data = [];
	if(dataType == "") data;

	if(dataType == CLAChart.DATA_TYPE_TOTAL) {
		data = this.charts[dataType];
	} else {
		if(platform == "") {
			return data;
		}
		data = this.charts[platform][dataType];
	}
	return data;
};
CLAPieChart.prototype.redrawByPoint = function(point, start, end) {
	var chart = null;
	var newDataType = CLAChart.DATA_TYPE_TOTAL;
	// When total data is currently shown in the chart, redraw (re-instanciate) chart with overview data
	if(this.dataType == CLAChart.DATA_TYPE_TOTAL) {
		this.selectedPlatform = point.name;
		newDataType = CLAChart.DATA_TYPE_OVERVIEW; // Set details to draw double pie chart
		chart = this.getChartData(this.selectedPlatform, CLAChart.DATA_TYPE_OVERVIEW);
	} else {
		newDataType = CLAChart.DATA_TYPE_TOTAL;
		chart = this.getChartData(null, CLAChart.DATA_TYPE_TOTAL);
	}
	this.redraw(chart, newDataType, true, start, end);
};
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
	if(this.dataType == CLAChart.DATA_TYPE_OVERVIEW || this.dataType == CLAChart.DATA_TYPE_DETAILS) {
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
				var date = series["date"][k];
				if(checkDate) {
					var d = date.split(",");
                    var utcDate = Date.UTC(d[0], d[1], d[2]);
					if(!this.isValidDate(utcDate, start, end)) {
						continue;
					}
				}

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
		if(this.dataType == CLAChart.DATA_TYPE_OVERVIEW || this.dataType == CLAChart.DATA_TYPE_DETAILS) {
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
				self.redrawByPoint(this, startDate, endDate);
			}
		}
	}
	return options;
};
CLABarChart.prototype.redrawByPoint = function(point, start, end) {
	var chart = null;
	var newDataType = CLAChart.DATA_TYPE_TOTAL;
	// When total data is currently shown in the chart, redraw (re-instanciate) chart with overview data
	if(this.dataType == CLAChart.DATA_TYPE_TOTAL) {
		this.selectedPlatform = point.series.name;
		newDataType = CLAChart.DATA_TYPE_OVERVIEW;
		chart = this.getChartData(this.selectedPlatform, CLAChart.DATA_TYPE_OVERVIEW);
	} else {
		newDataType = CLAChart.DATA_TYPE_TOTAL;
		chart = this.getChartData(null, CLAChart.DATA_TYPE_TOTAL);
	}
	this.redraw(chart, newDataType, true, start, end);
	this.dataType = newDataType;
};



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
		rangeSelector : { enabled: true, selected: 0, inputDateFormat: '%d/%m/%Y'},
		title : { enabled: false },
		yAxis: {
			height: 0,
			gridLineWidth: 0,
			labels: { enabled: true }
		},
		series: [],
		xAxis: {
			lineWidth: 0,
			tickLength : 0,
			labels: { enabled: false },
			events: {
				// Navigator range selector changed event handler
				afterSetExtremes: function (e) {
					startDate = e.min;
					endDate = e.max;
					for(key in chartObjDict) {
						var chartObj = chartObjDict[key];
						var chart = chartObj.getChartData(chartObj.selectedPlatform, chartObj.dataType);
						// Keep the values in global vals
						chartObj.redraw(chart, chartObj.dataType, true, e.min, e.max);
					}
				}
			}
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
				}
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
	var options = {
		type: this.chartType,
		name: category,
		center: [posX, null],
		size: diameter,
		dataLabels:{
			formatter: function () {
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
	url = "/dashboard/api/get_platform_activities/?course_code=" + course_code + "&platform=" + platform;
	var barChart = new CLABarChart("activityColumn", CLABarChartOptions.CHART_TYPE_COLUMN, "PROJ-TEAM2", "Trello", url);
	var pieChart = new CLAPieChart("activityPie", CLAPieChartOptions.CHART_TYPE_PIE, "PROJ-TEAM2", "Trello", url);
	CLAChart.saveChartObject(barChart);
	CLAChart.saveChartObject(pieChart);

	barChart.draw();
	pieChart.draw();
	navChart.changeChartAreaVisibility("activities", true);
	navChart.draw();
});
