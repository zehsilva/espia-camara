select p.nome_partido, dp.data_saida from partidos as p, deputados_partidos as dp where dp.id_partido = p.id_partido and dp.id_deputado = 74400;

select  d.nome_completo, sum(p.nome_partido) from deputados as d, deputados_partidos as dp, partidos as p where dp.id_deputado = d.id_deputado and dp.id_partido = p.id_partido group by dp.id_deputado;

select id_deputado from deputados_partidos group by id_deputado having count(id_deputado) > 3 order by id_deputado;

select p.nome_partido, DATE_FORMAT(dp.data_saida, '%d/%m/%Y') from partidos as p, deputados_partidos as dp where dp.id_partido = p.id_partido and dp.id_deputado = 74103;

select nome, latitude, longitude from municipios;

select m.latitude, m.longitude, dev.votos from deputados_eleicoes_votacoes dev, municipios m where dev.id_deputado = 74400 and dev.id_municipio = m.id_municipio;

select * from deputados_sessoes_presencas where id_deputado = 74400;

select * from deputados where nome_completo like '%tiririca%' or nome_parlamentar like '%tiririca%';

SELECT TP.palavra, TP.peso, T.id_topico
FROM ml_topicos_palavras AS TP,
	ml_topicos AS T,
	ml_discursos_topicos AS DT,
	discursos AS D
WHERE T.id_topico = TP.id_topico and
	DT.id_topico = T.id_topico and
	D.id_discurso = DT.id_discurso and
	D.id_deputado = 74400;
select * from ml_discursos_topicos;

SELECT dsp.data_reuniao, dsp.presenca
FROM deputados_sessoes_presencas as dsp
WHERE id_deputado = 74400;


