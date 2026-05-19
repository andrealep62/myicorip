SELECT replace(dbo.artico.ar_codart,',','_') AS [Codice Articolo], dbo.artico.ar_descr + ISNULL(dbo.artico.ar_desint, '') AS Descrizione, bc_code AS EAN13,
dbo.artico.ar_unmis AS UM, dbo.artico.ar_hhcodhhwb AS ID_Prodotto, dbo.artico.ar_hhvarwb AS ID_variante,dbo.artico.ar_hhdeshhwb AS Descr_web, CAST(dbo.artico.ar_hhpesotassabile AS DECIMAL(10,2)) AS pesotassabile,
CAST(ISNULL(listini.lc_prezzo, 0) AS DECIMAL(10,2)) AS Prezzo, CAST(ISNULL(listini.lc_prezzo, 0) AS DECIMAL(10,2)) AS PrezzoNoIva, CAST(22 AS DECIMAL(5,2)) AS Iva, CAST(ISNULL(artpro.ap_esist - artpro.ap_impeg, 0) AS INT) AS Dispnetta,
CAST(dbo.artico.ar_qtacon2 AS INT) AS Pack, dbo.artico.ar_hhnomeprodotto AS Prodotto, tabhhca.tb_deshhca AS Colore, dbo.artico.ar_hhqtacon4 AS Formato,
dbo.artico.ar_gruppo AS Gruppo, dbo.artico.ar_sotgru AS S_Gruppo
FROM     dbo.artico
LEFT JOIN barcode on ar_codart = bc_codart
LEFT OUTER JOIN (SELECT codditt, ap_codart, ap_magaz, ap_esist, ap_prenot, ap_ordin, ap_impeg, ap_carfor, ap_carpro, ap_carvar, ap_rescli, ap_scacli, ap_scapro,
ap_scavar, ap_resfor, ap_giaini, ap_vprenot, ap_vordin, ap_vimpeg, ap_vcarfor, ap_vcarpro, ap_vcarvar, ap_vrescli, ap_vscacli, ap_vscapro, ap_vscavar, ap_vresfor,
ap_vgiaini, ap_sommat, ap_daordi, ap_vdaordi, ap_fase, ap_ultagg
FROM      dbo.artpro AS artpro_1
WHERE   (ap_magaz = 1)) AS artpro ON artpro.codditt = dbo.artico.codditt AND artpro.ap_codart = dbo.artico.ar_codart
LEFT OUTER JOIN  (SELECT codditt, lc_progr, lc_codart, lc_codlavo, lc_conto, lc_codvalu, lc_codtpro, lc_listino, lc_datagg,
lc_tipo, lc_prezzo, lc_datscad, lc_daquant, lc_aquant, lc_perqta, lc_unmis, lc_note, lc_netto, lc_fase, lc_ultagg, lc_codcas,
lc_coddest
FROM      dbo.listini AS listini_1
WHERE   (lc_listino = 1)
AND CAST(GETDATE() AS DATE) BETWEEN CAST (lc_datagg AS DATE) AND CAST (lc_datscad AS DATE)) AS listini ON listini.codditt = dbo.artico.codditt AND
listini.lc_codart = dbo.artico.ar_codart
LEFT JOIN tabmarc ON tabmarc.codditt = artico.codditt AND tabmarc.tb_codmarc = artico.ar_codmarc
LEFT JOIN tabhhca ON tabhhca.tb_codhhca = artico.ar_hhcolore
WHERE  (ISNULL(dbo.artico.ar_hhflwb, 'N') = 'S')