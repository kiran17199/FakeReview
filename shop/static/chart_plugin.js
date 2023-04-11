




   function drawLineGraph(data) {
      var labels = data.labels;
      var chartLabel = data.chartLabel;
      var chartdata = data.chartdata;
      var ctx = document.getElementById('myChartline').getContext('2d');
      var chart = new Chart(ctx, { type: 'line', data: {
          labels: labels,
          datasets: [{
            label: chartLabel,
            backgroundColor: 'rgb(255, 100, 200)',
            borderColor: 'rgb(55, 99, 132)',
            data: chartdata,
          }]
        },
  
          options: {
        plugins: {
           title: {
        text: "Price Prediction",
        display: true
     }
        },
        scales: {
            x: {
               display:true,
                title: {
          color: 'Blue',
          display: true,
          text: 'Month'
        }
            },
            y: {
                display:true,
                ticks: {
                    // Include a dollar sign in the ticks
                    callback: function(value, index, ticks) {
                        return 'Rs ' + value;
                    }},
                 beginAtZero: true,
                 prefix: "Rs",  
                  title: {
          color: 'Blue',
          display: true,
          text: 'Price'
        }
            }
        }
    }
  
      });
    }