<!DOCTYPE html>
<html>
  <head>
    <title>Espia Câmara - Página Inicial</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="http://netdna.bootstrapcdn.com/bootstrap/3.0.1/css/bootstrap.min.css" rel="stylesheet" media="screen">
    <!--[if lt IE 9]>
      <script src="https://oss.maxcdn.com/libs/html5shiv/3.7.0/html5shiv.js"></script>
      <script src="https://oss.maxcdn.com/libs/respond.js/1.3.0/respond.min.js"></script>
    <![endif]-->
    <script src="/lib/d3/d3.js"></script>
    <script src="d3.layout.cloud.js"></script>
    <script src="https://code.jquery.com/jquery.js"></script>
  </head>
  <body>
    <?php include 'navbar.php';?>
    <div class="jumbotron">
      <div class="container">
        <h2>Espia Câmara</h2>
        <p>Se você sempre quis espiar o que anda acontecendo na câmara dos deputados, essa é sua chance!
          O Espia Câmara é um site que está de olho na atuação parlamentar de uma forma que nem os deputados estão!
        </p>
        <p>Nós utilizamos técnicas de inteligência artificial (<i>mineração de dados</i>) para detectar padrões nos dados abertos da câmara.
          Logo abaixo temos uma nuvem de tópicos extraídos automaticamente de todas as proposições e discursos. Por que você não clica num desses tópicos para ver que deputados estão se preocupando com isso?
          Você também pode pesquisar por um deputado na caixa ali em cima.</p>
        <p><a class="btn btn-primary btn-lg" role="button" href="/sobre">Para mais detalhes, acesse a página Sobre &raquo;</a></p>
      </div>
    </div>
    <div class="container">
      <div id="aqui">
        <img src="/img/loading.gif" width="200px" style="display: block; margin-left: auto; margin-right: auto;"/>
      </div>
      <script>
        $.getJSON("/getTopicosHome", function(data) {
          if (data.length > 0){
            var fill = d3.scale.category20();
            var h = 600; var halfH = 300;
            var w = $('#aqui').width(); var halfW = Math.round(w/2);
            var t = "translate(" + halfW.toString() + "," + (halfH).toString() + ")";
            d3.layout.cloud().size([w, h])
                .words(data)
                .padding(2)
                .rotate(function() { return ~~(Math.random() * 2) * 90; })
                .font("Impact")
                .fontSize(function(d) { return d.size; })
                .on("end", function(words){
                  $('#aqui').empty();
                  d3.select("#aqui").append("svg")
                    .attr("width", w)
                    .attr("height", h)
                  .append("g")
                    .attr("transform", t)
                  .selectAll("text")
                    .data(words)
                  .enter().append("text")
                    .style("font-size", function(d) { return d.size + "px"; })
                    .style("font-family", "Impact")
                    .style("fill", function(d, i) { return fill(i); })
                    .attr("text-anchor", "middle")
                    .attr("transform", function(d) {
                      return "translate(" + [d.x, d.y] + ")rotate(" + d.rotate + ")";
                    })
                  .append("a")
                    .attr("xlink:href", function(d) {return "/topico/" + d.id;})
                  .text(function(d) { return d.text; });
                })
                .start();
          } else {
            var div = document.getElementById('aqui');
            div.innerHTML = "Desculpa, algum erro aconteceu e não conseguimos recuperar os tópicos. Já estamos resolvendo isso. Mas você pode pesquisar por um deputado na caixa lá em cima no site!";
          }
        });
      </script>
    </div>
    <?php include('footer.php');?>
  </body>
</html>
