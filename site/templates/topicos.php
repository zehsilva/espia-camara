<!DOCTYPE html>
<html>
  <head>
    <title>Deputado Mining - Sobre</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <!-- Bootstrap -->
    <link href="http://netdna.bootstrapcdn.com/bootstrap/3.0.1/css/bootstrap.min.css" rel="stylesheet" media="screen">

    <!-- HTML5 Shim and Respond.js IE8 support of HTML5 elements and media queries -->
    <!-- WARNING: Respond.js doesn't work if you view the page via file:// -->
    <!--[if lt IE 9]>
      <script src="https://oss.maxcdn.com/libs/html5shiv/3.7.0/html5shiv.js"></script>
      <script src="https://oss.maxcdn.com/libs/respond.js/1.3.0/respond.min.js"></script>
    <![endif]-->
    <script src="../lib/d3/d3.js"></script>
    <script src="../d3.layout.cloud.js"></script>
  </head>
  <body>
    <?php include('navbar.php'); ?>
    <div class="jumbotron">
      <div class="container">
        <h2>Tópicos de interesse dos deputados</h2>
        <p>Essa é a nuvem de tópicos de todas as atuações dos deputados na câmara (proposições de leis ou discursos). Quer se aprofundar em algum tema? Basta clicar no tópico desejado e ver as proposições / discursos.</p>
        <div class="btn-group">
          <button type="button" class="btn btn-default">Proposições</button>
          <button type="button" class="btn btn-default">Discursos</button>
        </div>
      </div>
    </div>
    <div class="container" style="padding-top: 50px;">
      <div id="aqui"></div>
        <script>
          var fill = d3.scale.category20();
          <?php //var_dump($dados);?>
          d3.layout.cloud().size([300, 300])
              .words([<?php foreach ($dados as $key) { echo('{text:"'. str_replace(',', '_', $key[2]) . '", size:' . $key[1] . '*90}, '); }?>])
              // .words(["Educação", "Social", "defesa", "mineração", "acessibilidade", "testes", "professores", "aluno", "salário"].map(function(d) {
              //   return {text: d, size: 10 + Math.random() * 90};
              // }))
              .padding(5)
              .rotate(function() { return ~~(Math.random() * 2) * 90; })
              .font("Impact")
              .fontSize(function(d) { return d.size; })
              .on("end", draw)
              .start();

          function draw(words) {
            d3.select("#aqui").append("svg")
                .attr("width", 300)
                .attr("height", 300)
              .append("g")
                .attr("transform", "translate(150,150)")
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
                  .attr("xlink:href", function(d) {return "/topico/" + d.text + "/proposicoes";})
                .text(function(d) { return d.text; });
          }
        </script>
      </div>
    <?php include('footer.php'); ?>
  </body>
</html>
