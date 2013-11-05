<!DOCTYPE html>
<html>
  <head>
    <title>EspiaCâmara</title>
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
    <!-- jQuery (necessary for Bootstrap's JavaScript plugins) -->
    <script src="https://code.jquery.com/jquery.js"></script>
    <script type="text/javascript" src="https://www.google.com/jsapi"></script>
    <script>
      function carregaTopicosProposicoes(){
        var fill = d3.scale.category20();
        //Pegando os tópicos
        $.ajax({
            type: 'GET',
            url: '/getTopicosProposicoesDeputado/' + "<?php echo $id; ?>",
            dataType: "json",
            success: function(data, textStatus, jqXHR){
              if (data.length > 0){
                d3.layout.cloud().size([300, 300])
                    .words(jQuery.parseJSON(data))
                    .padding(5)
                    .rotate(function() { return ~~(Math.random() * 2) * 90; })
                    .font("Impact")
                    .fontSize(function(d) { return d.size; })
                    .on("end", draw)
                    .start();

                function draw(words) {
                  d3.select("#topicos_proposicoes").append("svg")
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
              } else {
                var div = document.getElementById('panel_topicos_proposicoes');
                div.innerHTML = 'Desculpa, ainda não calculamos os tópicos desse deputado. Já estamos trabalhando nesse problema :-/';
              }
            },
            error: function(jqXHR, textStatus, errorThrown){
              var div = document.getElementById('panel_topicos_proposicoes');
              div.innerHTML = 'Desculpa, não conseguimos recuperar os tópicos desse deputado. Já estamos trabalhando nesse problema :-/';
            }
        });
      }

      function carregaTopicosDiscursos(){
        var fill = d3.scale.category20();
        //Pegando os tópicos
        $.ajax({
            type: 'GET',
            url: '/getTopicosDiscursosDeputado/' + "<?php echo $id; ?>",
            dataType: "json", // data type of response
            success: function(data, textStatus, jqXHR){
              if (data.length > 0){
                d3.layout.cloud().size([300, 300])
                    .words(jQuery.parseJSON(data))
                    .padding(5)
                    .rotate(function() { return ~~(Math.random() * 2) * 90; })
                    .font("Impact")
                    .fontSize(function(d) { return d.size; })
                    .on("end", draw)
                    .start();

                function draw(words) {
                  d3.select("#topicos_proposicoes").append("svg")
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
                        .attr("xlink:href", function(d) {return "/topico/" + d.text + "/discursos";})
                      .text(function(d) { return d.text; });
                }
              } else {
                var div = document.getElementById('panel_topicos_discursos');
                div.innerHTML = 'Desculpa, não calculamos os tópicos desse deputado. Já estamos trabalhando nesse problema :-/';
              }
            },
            error: function(jqXHR, textStatus, errorThrown){
              var div = document.getElementById('panel_topicos_discursos');
              div.innerHTML = 'Desculpa, não conseguimos recuperar os tópicos desse deputado. Já estamos trabalhando nesse problema :-/';
            }
        });
      }

      function carregaVotosDeputado(){
        var div = document.getElementById('map-canvas');
        if ($('#map-canvas').is(':empty')){
          $.ajax({
            type: 'GET',
            url: '/getVotosDeputado/' + <?php echo $id ?>,
            dataType: "json",
            success: function(result){
              dados = result;//jQuery.parseJSON(result);
              if (dados.length > 0){
                var cidades = new Array();
                for (var i = 0; i < dados.length; i++) {
                  for (var j = 0; j < dados[i].votos; j++){
                    cidades.push(new google.maps.LatLng(dados[i].latitude, dados[i].longitude));
                  }
                }
                var mapOptions = {
                  zoom: 4,
                  center: new google.maps.LatLng(-15, -45),
                  mapTypeId: google.maps.MapTypeId.HYBRID
                };
                map = new google.maps.Map(document.getElementById('map-canvas'), mapOptions);
                var pointArray = new google.maps.MVCArray(cidades);
                heatmap = new google.maps.visualization.HeatmapLayer({ data: pointArray });
                heatmap.setOptions({radius: 20});
                heatmap.setMap(map);
              } else {
                var div = document.getElementById('map-canvas');
                div.innerHTML = 'Desculpa, não conseguimos recuperar dados da eleição desse deputado. Já estamos trabalhando nesse problema :-/';
              }
            },
            error: function(jqXHR, textStatus, errorThrown){
              var div = document.getElementById('map-canvas');
              div.innerHTML = 'Desculpa, não conseguimos recuperar dados da eleição desse deputado. Já estamos trabalhando nesse problema :-/';
            }
          });
        }
      }

      function carregaPresencas(){
        $.ajax({
            type: 'POST',
            contentType: 'application/json',
            url: '/getPresencasDeputado/' + <?php echo $id ?>,
            dataType: "json",
            success: function(data, textStatus, jqXHR){
              if (data.length > 0){
                google.load("visualization", "1", {packages:["corechart"]});
                google.setOnLoadCallback(drawChart);
                var options = {
                  title: 'Quantidade de faltas em sessões por mês'
                };

                var chart = new google.visualization.LineChart(document.getElementById('sessoes'));
                chart.draw(data, options);
                alert('teste');
              } else {
                var div = document.getElementById('sessoes');
                div.innerHTML = 'Esse deputado está de parabéns! Segundo nossa base de dados ele ainda não faltou nenhuma vez!';
              }
            },
            error: function(jqXHR, textStatus, errorThrown){
                var div = document.getElementById('sessoes');
                div.innerHTML = 'Desculpa, não conseguimos recuperar as faltas desse deputado. Já estamos trabalhando nesse problema :-/';
            }
        });
      }
    </script>
  </head>
  <body>
    <?php include 'navbar.php';?>

    <div class="container" style="padding-top: 60px;">
      <div class="row">
        <div class="col-sm-6 col-md-3">
          <a href="#" class="thumbnail">
            <img src="<?php echo $url_foto;?>" alt="Deputado">
          </a>
        </div>
        <div class="col-md-4">
          <h3><?php echo $nome_parlamentar;?></h3>
          <dl class="dl-horizontal">
            <dt>Eleito pelo estado:</dt>
            <dd><?php echo $uf;?></dd>
            <dt>Eleito pelo partido:</dt>
            <dd><?php echo $eleicao_partido;?></dd>
            <dt>Partido atual:</dt>
            <dd><?php echo $partido_atual;?></dd>
          </dl>
        </div>
        <div class="col-md-4">
          <h3>Mandatos</h3>
          <table class="table table-condensed">
            <thead>
              <tr>
                <th>Ano</th>
              </tr>
            </thead>
            <tbody>
              <?php foreach ($mandatos as $key) { echo('<tr><td>' . $key[0] . '-' . ($key[0] + 3) . '</td></tr>'); } ?>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <div class="container">
      <div class="panel-group" id="accordion">
        <div class="panel panel-default">
          <div class="panel-heading">
            <h2 class="panel-title">
              <a data-toggle="collapse" data-parent="#accordion" href="#topicos_proposicoes" onclick="carregaTopicosProposicoes()">
                Quais são os tópicos das proposições desse deputado?
              </a>
            </h2>
          </div>
          <div id="topicos_proposicoes" class="panel-collapse collapse">
            <div class="panel-body" id="panel_topicos_proposicoes">
              <p>Clique em um tópico para ver os deputados semelhantes:</p>
            </div>
          </div>
        </div>
        <div class="panel panel-default">
          <div class="panel-heading">
            <h2 class="panel-title">
              <a data-toggle="collapse" data-parent="#accordion" href="#topicos_discursos" onclick="carregaTopicosDiscursos();">
                Quais são os tópicos dos discursos desse deputado?
              </a>
            </h2>
          </div>
          <div id="topicos_discursos" class="panel-collapse collapse">
            <div class="panel-body" id="panel_topicos_discursos">
              <p>Clique em um tópico para ver os deputados semelhantes:</p>
            </div>
          </div>
        </div>
        <div class="panel panel-default">
          <div class="panel-heading">
            <h2 class="panel-title">
              <a data-toggle="collapse" data-parent="#accordion" href="#presenca_sessao" onclick="carregaPresencas();">
                Esse deputado anda faltando as sessões?
              </a>
            </h2>
          </div>
          <div id="presenca_sessao" class="panel-collapse collapse">
            <div class="panel-body">
              <div id="sessoes" style="width: 100%; height: 500px;"></div>
            </div>
          </div>
        </div>
        <div class="panel panel-default">
          <div class="panel-heading">
            <h2 class="panel-title">
              <a data-toggle="collapse" data-parent="#accordion" href="#quem_votou" onclick="carregaVotosDeputado();">
                Quem elegeu esse deputado?
              </a>
            </h2>
          </div>
          <div id="quem_votou" class="panel-collapse collapse">
            <div class="panel-body">
              <p>Aguarde o mapa carregar. Os pontos mais vermelhos indicam maior quantidade de votos.</p>
              <div id="map-canvas" style="width:100%; height:400px; align: center;"></div>
            </div>
          </div>
        </div>
        <div class="panel panel-default">
          <div class="panel-heading">
            <h2 class="panel-title">
              <a data-toggle="collapse" data-parent="#accordion" href="#historico_partido">
                Esse deputado já mudou muito de partido?
              </a>
            </h2>
          </div>
          <div id="historico_partido" class="panel-collapse collapse">
            <div class="panel-body">
              <?php if (!empty($trocas)){ ?>
                <p>Esse é o histórico de mudanças de partido desse deputado.</p>
                <table class="table table-condensed">
                  <thead>
                    <tr>
                      <th>Partido</th>
                      <th>Data de saída</th>
                    </tr>
                  </thead>
                  <tbody>
                    <?php foreach ($trocas as $troca) { echo('<tr><td>' . $troca[0] . '</td><td>' . $troca[1] . '</td></tr>'); } ?>
                  </tbody>
                </table>
              <?php } else { ?>
                <p>Não há registro de troca de partido.</p>
              <?php } ?>
            </div>
          </div>
        </div>
        <div class="panel panel-default">
          <div class="panel-heading">
            <h2 class="panel-title">
              <a data-toggle="collapse" data-parent="#accordion" href="#info_contato">
                Como posso saber mais sobre o deputado e entrar em contato com ele?
              </a>
            </h2>
          </div>
          <div id="info_contato" class="panel-collapse collapse">
            <div class="panel-body">
              <div class="row">
                <div class="col-md-4">
                  <dl class="dl-horizontal">
                    <dt>Nome completo</dt>
                    <dd><?php echo $nome_completo;?></dd>
                    <dt>Data de nascimento:</dt>
                    <dd><?php echo $data_nascimento;?></dd>
                    <dt>Profissão:</dt>
                    <dd><?php echo $nome_profissao;?></dd>
                    <dt>Título eleitoral:</dt>
                    <dd><?php echo $titulo_eleitoral;?></dd>
                    <dt>CPF:</dt>
                    <dd><?php echo $cpf;?></dd>
                    <dt>Sexo:</dt>
                    <dd><?php echo $sexo;?></dd>
                  </dl>
                </div>
                <div class="col-md-4">
                  <dl class="dl-horizontal">
                    <dt>Site</dt>
                    <dd><?php echo '<a target="_blank" href="http://www.camara.gov.br/internet/Deputado/dep_Detalhe.asp?id=' . $id . '">Página na Câmara</a>';?></dd>
                    <dt>E-mail</dt>
                    <dd><?php echo $email;?></dd>
                    <dt>Gabinete:</dt>
                    <dd><?php echo $gabinete;?></dd>
                    <dt>Facebook:</dt>
                    <dd><?php echo $url_facebook;?></dd>
                    <dt>Twitter:</dt>
                    <dd><?php echo $url_twitter;?></dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

    </div>
    <script src="https://maps.googleapis.com/maps/api/js?v=3.exp&sensor=false&libraries=visualization"></script>
    <?php include('footer.php');?>
  </body>
</html>
