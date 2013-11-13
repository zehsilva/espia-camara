<!DOCTYPE html>
<html>
  <head>
    <title>Deputado Mining - Sobre o Site</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <!-- Bootstrap -->
    <link href="http://netdna.bootstrapcdn.com/bootstrap/3.0.1/css/bootstrap.min.css" rel="stylesheet" media="screen">

    <!-- HTML5 Shim and Respond.js IE8 support of HTML5 elements and media queries -->
    <!-- WARNING: Respond.js doesn't work if you view the page via file:// -->
    <!--[if lt IE 9]>
      <script src="https://oss.maxcdn.com/libs/html5shiv/3.7.0/html5shiv.js"></script>
      <script src="https://oss.maxcdn.com/libs/respond.js/1.3.0/respond.min.js"></script>
    <![endif]-->
  </head>
  <body>
    <?php include 'navbar.php';?>
    <div class="container">

      <div class="page-header">
        <h1>O que é a coclusterização?</h1>
      </div>
    <div>
          <p>A descoberta automática de bancadas utilizou uma técnica de mineração de dados conhecida como biclusterização. No jeito chato de explicar, temos como entrada uma matriz de dados e tentamos encontrar submatrizes altamente relacionadas. Vamos exemplificar. Suponha que você tem uma loja onde aluga filmes e seus clientes avaliam os filmes que assistiram. Nesse caso, poderíamos montar uma matriz de dados onde cada linha representa um cliente e cada coluna representa um filme. Cada valor nessa matriz corresponde a nota que o cliente i deu ao filme j. Essa forma de representar os dados é muito interessante pois dela podemos extrair muitas análises interessantes. E é aqui que surge uma pergunta interessante:</p>

        <blockquote>Não seria interessante criar grupos de clientes que avaliam os filmes da mesma forma? Assim, se um cliente ainda não viu um filme bem avaliado por clientes no mesmo grupo que ele, poderíamos sugerí-lo alugar esse filme!</blockquote>

        <p>Para fazer esse agrupamento se utilizam técnicas de clusterização, que conseguem agrupar as linhas da nossa matriz que possuem valores semelhantes em todas as suas colunas. Mas se formos pensar mais um pouco, já temos outra pergunta:</p>

        <blockquote>E se um cliente avalia filmes de “ação” da mesma forma que um grupo, mas avalia filmes de “terror” da mesma forma que outro grupo completamente diferente, colocamos esse cliente em que grupo?</blockquote>

        <p>Aqui entra a biclusterização. Com essa técnica somos capazes de encontrar grupos de clientes que avaliam filmes de um grupo de categorias da mesma forma. Por exemplo, um grupo teria os clientes que avaliam filmes de “ação” da mesma forma, outro grupo teria os clientes que avaliam os filmes de “terror” de forma semelhante, e por aí vai. Vale ressaltar duas propriedades interessantes que esse novo modelo nos traz:</p>
        <li>
          <ol>Fica evidente que tipos de filme são relevantes para o grupo.</ol>
          <ol>Um cliente pode estar em vários grupos distintos.</ol>
        </li>

        <p>Por isso a biclusterização é uma técnica muito interessante para descobrir bancadas de deputados pois uma bancada nada mais é que um grupo de deputados que vota de forma semelhante num grupo de proposições. Veja, eles podem até votar de forma diferente em outro grupo de proposições, mas para o grupo detectado eles votam de forma semelhante.</p>
    </div>

    <div class="page-header">
        <h1>Como fizemos nossa análise?</h1>
      </div>
    <div>
        <p>Existem diversos algoritmos de biclusterização, e para analisar os dados abertos da câmara, escolhemos utilizar o Spectral Coclustering proposto por Dhillon em 2011. A matriz de dados foi montada da seguinte forma: Pegamos todas as votações desde 2007 e todos os deputados que participaram dessas votações de alguma forma (votado sim, votado não ou se abstiveram). Então na matriz, cada linha representa um deputado, cada coluna uma votação e os valores: 1 para sim, 0 para não e 0.5 para abstenção. Os melhores resultados apareceram quando o algoritmo foi configurado para encontrar 15 grupos.</p>
        <p>Para facilitar a interpretação, a Figura 1 mostra a  matriz de dados original. A cor rosa representa os votos não, branco as ausências ou abstenções e a cor verde representa os votos sim.</p>
        <img src="" />
        <p>Após a biclusterização, a matriz ficou como na Figura 2. É possível perceber que existem grupos muito bem destacados. Esses grupos onde uma cor predomina são os biclusters (grupos).</p>
        <img src="" />
    </div>
    <div class="page-header">
        <h1>Ok, entendi, mas o que dá pra inferir com isso?</h1>
      </div>
    <div>
      <p>Mesmo sem entrar em muitos detalhes, pelas imagens dá pra inferir algumas coisas interessantes. Por exemplo, é possível perceber que quando existe um quadrado rosa, poucos lugares possuem outro quadrado verde nas mesmas linhas ou colunas. Isso indica que quando os deputados votam nessas proposições, geralmente há consenso, pois não há outro grupo que vote diferente.</p>
    <p>Outras conclusões interessantes podem ser derivadas ao ver os dados dos deputados de um grupo só. Percebemos que os biclusters são bem coerentes em relação a partidos de oposição ou situação, etc.</p>
    </div>
    <div class="page-header">
        <h1>Como eu vejo esses resultados no site Espia Câmara?</h1>
      </div>
    <div>
      <p>Esses resultados foram implementados como bancadas no site. Você pode clicar na opção “Bancadas” acima e ver os 15 grupos que encontramos.</p>
      <blockquote>E aí eu aproveito pra te lançar um desafio!<br/>
    Na página de cada bancada estão listados os deputados e as proposições de lei envolvidas. Que tal você tentar entender a relação entre esses deputados e essas proposições? Envie-nos a sua análise e podemos publicá-la aqui!</blockquote>
    </div>

    <div class="page-header">
        <h3>Referências</h3>
      </div>
    <div>
      <p>Inderjit S. Dhillon. 2001. Co-clustering documents and words using bipartite spectral graph partitioning. InProceedings of the seventh ACM SIGKDD international conference on Knowledge discovery and data mining(KDD '01). ACM, New York, NY, USA, 269-274. DOI=10.1145/502512.502550 http://doi.acm.org/10.1145/502512.502550</p>
    </div>
    </div>
    <script src="https://code.jquery.com/jquery.js"></script>
    <?php include('footer.php');?>
  </body>
</html>