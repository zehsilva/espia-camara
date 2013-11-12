<!DOCTYPE html>
<html>
  <head>
    <title>EspiaC�mara - Perfil de <?php echo($deputado['nome_parlamentar'])?></title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="http://netdna.bootstrapcdn.com/bootstrap/3.0.1/css/bootstrap.min.css" rel="stylesheet" media="screen">
    <!-- HTML5 Shim and Respond.js IE8 support of HTML5 elements and media queries -->
    <!-- WARNING: Respond.js doesn't work if you view the page via file:// -->
    <!--[if lt IE 9]>
      <script src="https://oss.maxcdn.com/libs/html5shiv/3.7.0/html5shiv.js"></script>
      <script src="https://oss.maxcdn.com/libs/respond.js/1.3.0/respond.min.js"></script>
    <![endif]-->
    <script src="../lib/d3/d3.js"></script>
    <script src="../d3.layout.cloud.js"></script>
    <script src="https://code.jquery.com/jquery.js"></script>
    <script>
      function carregaTopicosProposicoes(){
        if ($('#panel_topicos_proposicoes').is(':empty')){
          $.getJSON("/getTopicosProposicoesDeputado/<?php echo $deputado['id']?>", function( data ) {
            if (data.length > 0){
              var fill = d3.scale.category20();
              var h = 300; var halfH = 150;
              var w = $('#panel_topicos_proposicoes').width(); var halfW = Math.round(w/2);
              var t = "translate(" + halfW.toString() + "," + (halfH).toString() + ")";
              d3.layout.cloud().size([w, h])
                  .words(data)
                  .padding(5)
                  .rotate(function() { return ~~(Math.random() * 2) * 90; })
                  .font("Impact")
                  .fontSize(function(d) { return d.size; })
                  .on("end", function(words){
                    $('#msg_topicos_proposicoes').empty();
                    d3.select("#panel_topicos_proposicoes").append("svg")
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
                            .append("a").attr("xlink:href", function(d) {return "/topico/" + d.id;})
                            .text(function(d) { return d.text; });
                  })
                  .start();

            } else {
              var div = document.getElementById('msg_topicos_proposicoes');
              div.innerHTML = 'Esse deputado ainda n�o fez nenhuma proposi��o, por isso n�o temos seus t�picos :-).';
            }
          });
        }
      }
      function carregaTopicosDiscursos(){
        if ($('#panel_topicos_discursos').is(':empty')){
          $.getJSON("/getTopicosDiscursosDeputado/<?php echo $deputado['id']?>", function( data ) {
            if (data.length > 0){
              var fill = d3.scale.category20();
              var h = 300; var halfH = 150;
              var w = $('#panel_topicos_discursos').width(); var halfW = Math.round(w/2);
              var t = "translate(" + halfW.toString() + "," + (halfH).toString() + ")";
              d3.layout.cloud().size([w, h])
                  .words(data)
                  .padding(5)
                  .rotate(function() { return ~~(Math.random() * 2) * 90; })
                  .font("Impact")
                  .fontSize(function(d) { return d.size; })
                  .on("end", function(words){
                    $('#msg_topicos_discursos').empty();
                    d3.select("#panel_topicos_discursos").append("svg")
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
              var div = document.getElementById('msg_topicos_discursos');
              div.innerHTML = 'Esse deputado ainda n�o fez nenhum discurso, por isso n�o temos seus t�picos :-).';
            }
          });
        }
      }
      function carregaVotosDeputado(){
        if ($('#map-canvas').is(':empty')){
          $.ajax({
            type: 'GET',
            url: '/getVotosDeputado/' + <?php echo $deputado['id'] ?>,
            dataType: "json",
            success: function(result){
              dados = result;
              $('#loading').empty();
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
                div.innerHTML = 'Desculpa, n�o conseguimos recuperar dados da elei��o desse deputado. J� estamos trabalhando nesse problema :-/';
              }
            },
            error: function(jqXHR, textStatus, errorThrown){
              var div = document.getElementById('map-canvas');
              div.innerHTML = 'Desculpa, n�o conseguimos recuperar dados da elei��o desse deputado. J� estamos trabalhando nesse problema :-/';
        ����}
          });
        }
      }
      function carregaPresencas(){
        $.ajax({
            type: 'GET',
            url: '/getPresencasDeputado/' + <?php echo $deputado['id'] ?>,
            dataType: "json",
            success: function(data, textStatus, jqXHR){
              if (data.length > 0){
                var div = document.getElementById('sessoes');
                var texto = "<table class='table table-condensed'><thead><tr><th>M�s em que houveram faltas</th><th>Qtde de faltas</th></thead><tbody>";
                for (var i = 0; i < data.length; i++) {
                  element = data[i];
                  texto = texto + "<tr><td>" + element['data'] + "</td><td>" + element['faltas'] + "</td></tr>";
                }
                var texto = texto + "</tbody></table>";
                div.innerHTML = texto;

              } else {
                var div = document.getElementById('sessoes');
                div.innerHTML = 'Esse deputado est� de parab�ns! Segundo nossa base de dados ele ainda n�o faltou nenhuma vez!';
              }
            },
            error: function(jqXHR, textStatus, errorThrown){
                alert(errorThrown);
                var div = document.getElementById('sessoes');
                div.innerHTML = 'Desculpa, n�o conseguimos recuperar as faltas desse deputado. J� estamos trabalhando nesse problema :-/';
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
          <img src="<?php echo $deputado['url_foto'];?>" alt="Deputado" class="thumbnail">
        </div>
        <div class="col-md-4">
          <h3><?php echo $deputado['nome_parlamentar'];?></h3>
          <dl class="dl-horizontal">
            <dt>Eleito pelo estado:</dt>
            <dd><?php echo $deputado['uf'];?></dd>
            <dt>Eleito pelo partido:</dt>
            <dd><?php echo $deputado['eleicao_partido'];?></dd>
            <dt>Partido atual:</dt>
            <dd><?php echo $deputado['partido_atual'];?></dd>
              <?php if ($deputado['id_bicluster']) { ?>
                <dt>Bancada:</dt>
                  <dd>
                    <a href="/bancada/<?php echo $deputado['id_bicluster']?>"
                      target="_blank" class="btn btn-danger">
                      Bancada <?php echo $deputado['id_bicluster'] + 1?>
                    </a>
              <?php }?>
            </dd>
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
                Quais s�o os t�picos das proposi��es desse deputado?
              </a>
            </h2>
          </div>
          <div id="topicos_proposicoes" class="panel-collapse collapse">
            <div class="panel-body">
              <p>Clique em um t�pico para ver outros deputados relacionados.</p>
              <div  id="msg_topicos_proposicoes">
                <img src="/img/loading.gif" width="100px" style="display: block; margin-left: auto; margin-right: auto;"/>
              </div>
              <div  id="panel_topicos_proposicoes"></div>
            </div>
          </div>
        </div>
        <div class="panel panel-default">
          <div class="panel-heading">
            <h2 class="panel-title">
              <a data-toggle="collapse" data-parent="#accordion" href="#topicos_discursos" onclick="carregaTopicosDiscursos();">
                Quais s�o os t�picos dos discursos desse deputado?
              </a>
            </h2>
          </div>
          <div id="topicos_discursos" class="panel-collapse collapse">
            <div class="panel-body">
              <p>Clique em um t�pico para ver outros deputados relacionados.</p>
              <div id="msg_topicos_discursos">
                <img src="/img/loading.gif" width="100px" style="display: block; margin-left: auto; margin-right: auto;"/>
              </div>
              <div  id="panel_topicos_discursos"></div>
            </div>
          </div>
        </div>
        <div class="panel panel-default">
          <div class="panel-heading">
            <h2 class="panel-title">
              <a data-toggle="collapse" data-parent="#accordion" href="#presenca_sessao" onclick="carregaPresencas();">
                Esse deputado anda faltando as sess�es?
              </a>
            </h2>
          </div>
          <div id="presenca_sessao" class="panel-collapse collapse">
            <div class="panel-body">
              <div id="sessoes">
                <img src="/img/loading.gif" width="100px" style="display: block; margin-left: auto; margin-right: auto;"/>
              </div>
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
              <div id="loading"><img src="/img/loading.gif" width="100px" style="display: block; margin-left: auto; margin-right: auto;"/></div>
              <div id="map-canvas" style="width:100%; height:400px; align: center;"></div>
            </div>
          </div>
        </div>
        <div class="panel panel-default">
          <div class="panel-heading">
            <h2 class="panel-title">
              <a data-toggle="collapse" data-parent="#accordion" href="#historico_partido">
                Esse deputado j� mudou muito de partido?
              </a>
            </h2>
          </div>
          <div id="historico_partido" class="panel-collapse collapse">
            <div class="panel-body">
              <?php if (!empty($trocas)){ ?>
                <p>Esse � o hist�rico de mudan�as de partido desse deputado.</p>
                <table class="table table-condensed">
                  <thead>
                    <tr>
                      <th>Partido</th>
                      <th>Data de sa�da</th>
                    </tr>
                  </thead>
                  <tbody>
                    <?php foreach ($trocas as $troca) { echo('<tr><td>' . $troca[0] . '</td><td>' . $troca[1] . '</td></tr>'); } ?>
                  </tbody>
                </table>
              <?php } else { ?>
                <p>N�o h� registro de troca de partido.</p>
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
                <div class="col-md-6">
                  <dl class="dl-horizontal">
                    <dt>Nome completo</dt>
                    <dd><?php echo $deputado['nome_completo'];?></dd>
                    <dt>Data de nascimento:</dt>
                    <dd><?php echo $deputado['data_nascimento'];?></dd>
                    <dt>Profiss�o:</dt>
                    <dd><?php echo $deputado['nome_profissao'];?></dd>
                    <dt>T�tulo eleitoral:</dt>
                    <dd><?php echo $deputado['titulo_eleitoral'];?></dd>
                    <dt>CPF:</dt>
                    <dd><?php echo $deputado['cpf'];?></dd>
                    <dt>Sexo:</dt>
                    <dd><?php echo $deputado['sexo'];?></dd>
                  </dl>
                </div>
                <div class="col-md-6">
                  <dl class="dl-horizontal">
                    <dt>Site</dt>
                    <dd><?php echo '<a target="_blank" href="http://www.camara.gov.br/internet/Deputado/dep_Detalhe.asp?id=' . $deputado['id'] . '">P�gina na C�mara</a>';?></dd>
                    <dt>E-mail</dt>
                    <dd><?php echo $deputado['email'];?></dd>
                    <dt>Gabinete:</dt>
                    <dd><?php echo $deputado['gabinete'];?></dd>
                    <dt>Facebook:</dt>
                    <dd><?php echo $deputado['url_facebook'];?></dd>
                    <dt>Twitter:</dt>
                    <dd><?php echo $deputado['url_twitter'];?></dd>
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
