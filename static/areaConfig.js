var colors = [
    'rgb(  0,   0, 255)',
    'rgb(  0, 203, 255)',
    'rgb(255, 255,   0)',
    'rgb(216, 255, 204)',
    'rgb(  0, 255,   0)',
    'rgb(  0, 101,   0)',
    'rgb(255, 63,    0)',
    'rgb( 203,  0, 203)',
    'rgb(  0,   0,  50)'
]

var trans = function(color, opacity) {
    var alpha = opacity === undefined ? 0.5 : 1 - opacity;
    return Color(color).alpha(alpha).rgbString();
}

function areaConfig(x, y){
  var data = {
    labels: x,
    datasets: []
  }
  for (i = 0; i< y.length; i++){
    var fill = true
    if(i > 0){
      fill = "-1"
    }
    val = Object.values(y[i])[0]
    val = val.slice(Math.max(val.length - x.length, 0) , val.length)
    data.datasets[i] = {
      backgroundColor: trans(colors[i % colors.length]),
      borderColor: colors[i % colors.length],
      data: val,
      label: Object.keys(y[i])[0],
      fill : fill
    }
  }
  var options = {
    elements: {
      line: {
        tension: 0.1
      }
    },
    scales: {
      yAxes: [{
        stacked: true,
        ticks: {
          beginAtZero: false
        }
      }]
    },
    legend: {
      display: true,
    }
  }
  var ret = {
    type: 'line',
    data: data,
    options: options
  }
  return ret
}