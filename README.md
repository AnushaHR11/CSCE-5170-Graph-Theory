# CSCE-5170-Graph-Theory
 $ python3 shakespeare_network.py --play hamlet

► Scraping «Hamlet» …
  Found 20 scenes.
  Parsing Act 1, Scene 1 … 4 characters, 189 lines
  Parsing Act 1, Scene 2 … 10 characters, 274 lines
  Parsing Act 1, Scene 3 … 3 characters, 140 lines
  Parsing Act 1, Scene 4 … 3 characters, 101 lines
  Parsing Act 1, Scene 5 … 3 characters, 216 lines
  Parsing Act 2, Scene 1 … 3 characters, 131 lines
  Parsing Act 2, Scene 2 … 7 characters, 623 lines
  Parsing Act 3, Scene 1 … 7 characters, 202 lines
  Parsing Act 3, Scene 2 … 9 characters, 390 lines
  Parsing Act 3, Scene 3 … 5 characters, 101 lines
  Parsing Act 3, Scene 4 … 3 characters, 242 lines
  Parsing Act 4, Scene 1 … 2 characters, 42 lines
  Parsing Act 4, Scene 2 … 5 characters, 30 lines
  Parsing Act 4, Scene 3 … 3 characters, 73 lines
  Parsing Act 4, Scene 4 … 3 characters, 68 lines
  Parsing Act 4, Scene 5 … 5 characters, 235 lines
  Parsing Act 4, Scene 6 … 1 characters, 33 lines
  Parsing Act 4, Scene 7 … 3 characters, 218 lines
  Parsing Act 5, Scene 1 … 5 characters, 242 lines
  Parsing Act 5, Scene 2 … 7 characters, 424 lines

════════════════════════════════════════════════════════════
  Character Network – Hamlet
════════════════════════════════════════════════════════════
  Nodes (characters) : 20
  Edges (co-scenes)  : 98

  Top 10 characters by lines spoken:
    HAMLET                          1759 lines  (13 scenes)
    KING CLAUDIUS                    571 lines  (11 scenes)
    LORD POLONIUS                    400 lines  (8 scenes)
    HORATIO                          295 lines  (9 scenes)
    LAERTES                          221 lines  (6 scenes)
    OPHELIA                          176 lines  (5 scenes)
    QUEEN GERTRUDE                   171 lines  (10 scenes)
    ROSENCRANTZ                       93 lines  (7 scenes)
    MARCELLUS                         62 lines  (4 scenes)
    GUILDENSTERN                      52 lines  (5 scenes)

  Top 10 character pairings by shared-line weight:
    KING CLAUDIUS          ↔  HAMLET                  weight= 1543  (8 shared scene(s))
    HAMLET                 ↔  QUEEN GERTRUDE          weight= 1480  (7 shared scene(s))
    HORATIO                ↔  HAMLET                  weight= 1236  (6 shared scene(s))
    LORD POLONIUS          ↔  HAMLET                  weight= 1230  (6 shared scene(s))
    HAMLET                 ↔  ROSENCRANTZ             weight=  890  (7 shared scene(s))
    HAMLET                 ↔  GUILDENSTERN            weight=  767  (5 shared scene(s))
    KING CLAUDIUS          ↔  QUEEN GERTRUDE          weight=  600  (9 shared scene(s))
    LAERTES                ↔  HAMLET                  weight=  585  (3 shared scene(s))
    KING CLAUDIUS          ↔  LAERTES                 weight=  528  (5 shared scene(s))
    KING CLAUDIUS          ↔  LORD POLONIUS           weight=  467  (5 shared scene(s))

  Avg. shortest path (largest component): 1.521
  Graph density                          : 0.5158
@AnushaHR11 ➜ /workspaces/CSCE-5170-Graph-Theory (main) $ python3 shakespeare_mention_network.py --play hamlet

► Scraping «Hamlet» …
  [ERROR] No scenes found for 'hamlet'.
@AnushaHR11 ➜ /workspaces/CSCE-5170-Graph-Theory (main) $ python3 shakespeare_mention_network.py --play hamlet

► Scraping «Hamlet» …
  Found 20 scenes.
                                                              
  Characters found: 20
  Alias patterns  : 62
                                                              
  Mention events  : 321

════════════════════════════════════════════════════════════
  Directed Mention Network – Hamlet
════════════════════════════════════════════════════════════
  Nodes (characters)  : 25
  Directed edges      : 83

  Top 10 characters by lines-in-speeches-that-mention-others:
    HAMLET                          1069 lines  (out-degree 12)
    KING CLAUDIUS                    842 lines  (out-degree 14)
    HORATIO                          259 lines  (out-degree 8)
    LORD POLONIUS                    249 lines  (out-degree 8)
    LAERTES                          118 lines  (out-degree 6)
    QUEEN GERTRUDE                    67 lines  (out-degree 7)
    VOLTIMAND                         42 lines  (out-degree 2)
    PRINCE FORTINBRAS                 28 lines  (out-degree 4)
    BERNARDO                          27 lines  (out-degree 4)
    OSRIC                             26 lines  (out-degree 4)

  Top 10 most-mentioned characters (weighted in-degree):
    CLAUDIUS                         515 weighted lines  (in-degree 12)
    HAMLET                           466 weighted lines  (in-degree 9)
    GERTRUDE                         457 weighted lines  (in-degree 7)
    GHOST                            380 weighted lines  (in-degree 7)
    OPHELIA                          211 weighted lines  (in-degree 5)
    LAERTES                          157 weighted lines  (in-degree 5)
    HORATIO                          134 weighted lines  (in-degree 4)
    FORTINBRAS                       109 weighted lines  (in-degree 6)
    GUILDENSTERN                      73 weighted lines  (in-degree 6)
    MARCELLUS                         55 weighted lines  (in-degree 3)

  Top 10 directed mention arcs (by weight):
    HAMLET                 →  CLAUDIUS                weight=  346  mentions= 26
    HAMLET                 →  GERTRUDE                weight=  289  mentions= 30
    KING CLAUDIUS          →  HAMLET                  weight=  242  mentions= 27
    HAMLET                 →  GHOST                   weight=  215  mentions= 16
    KING CLAUDIUS          →  GERTRUDE                weight=  119  mentions= 13
    HAMLET                 →  HORATIO                 weight=  108  mentions= 17
    KING CLAUDIUS          →  GHOST                   weight=   90  mentions=  4
    LORD POLONIUS          →  HAMLET                  weight=   80  mentions=  7
    KING CLAUDIUS          →  LAERTES                 weight=   76  mentions= 11
    LORD POLONIUS          →  OPHELIA                 weight=   75  mentions=  7

  Reciprocal pairs     : 9 (21.7% of edges)
@AnushaHR11 ➜ /workspaces/CSCE-5170-Graph-Theory (main) $ python3 shakespeare_mention_network.py --play hamlet

► Scraping «Hamlet» …
  Found 20 scenes.
                                                              
  Characters found: 20
  Alias patterns  : 62
                                                              
  Mention events  : 321

════════════════════════════════════════════════════════════
  Directed Mention Network – Hamlet
════════════════════════════════════════════════════════════
  Nodes (characters)  : 25
  Directed edges      : 83

  Top 10 characters by lines-in-speeches-that-mention-others:
    HAMLET                          1069 lines  (out-degree 12)
    KING CLAUDIUS                    842 lines  (out-degree 14)
    HORATIO                          259 lines  (out-degree 8)
    LORD POLONIUS                    249 lines  (out-degree 8)
    LAERTES                          118 lines  (out-degree 6)
    QUEEN GERTRUDE                    67 lines  (out-degree 7)
    VOLTIMAND                         42 lines  (out-degree 2)
    PRINCE FORTINBRAS                 28 lines  (out-degree 4)
    BERNARDO                          27 lines  (out-degree 4)
    OSRIC                             26 lines  (out-degree 4)

  Top 10 most-mentioned characters (weighted in-degree):
    CLAUDIUS                         515 weighted lines  (in-degree 12)
    HAMLET                           466 weighted lines  (in-degree 9)
    GERTRUDE                         457 weighted lines  (in-degree 7)
    GHOST                            380 weighted lines  (in-degree 7)
    OPHELIA                          211 weighted lines  (in-degree 5)
    LAERTES                          157 weighted lines  (in-degree 5)
    HORATIO                          134 weighted lines  (in-degree 4)
    FORTINBRAS                       109 weighted lines  (in-degree 6)
    GUILDENSTERN                      73 weighted lines  (in-degree 6)
    MARCELLUS                         55 weighted lines  (in-degree 3)

  Top 10 directed mention arcs (by weight):
    HAMLET                 →  CLAUDIUS                weight=  346  mentions= 26
    HAMLET                 →  GERTRUDE                weight=  289  mentions= 30
    KING CLAUDIUS          →  HAMLET                  weight=  242  mentions= 27
    HAMLET                 →  GHOST                   weight=  215  mentions= 16
    KING CLAUDIUS          →  GERTRUDE                weight=  119  mentions= 13
    HAMLET                 →  HORATIO                 weight=  108  mentions= 17
    KING CLAUDIUS          →  GHOST                   weight=   90  mentions=  4
    LORD POLONIUS          →  HAMLET                  weight=   80  mentions=  7
    KING CLAUDIUS          →  LAERTES                 weight=   76  mentions= 11
    LORD POLONIUS          →  OPHELIA                 weight=   75  mentions=  7

  Reciprocal pairs     : 9 (21.7% of edges)
@AnushaHR11 ➜ /workspaces/CSCE-5170-Graph-Theory (main) $ python3 shakespeare_network.py --play macbeth
python3 shakespeare_network.py --play romeo_juliet

► Scraping «Macbeth» …
  Found 28 scenes.
  Parsing Act 1, Scene 1 … 0 characters, 0 lines
  Parsing Act 1, Scene 2 … 4 characters, 76 lines
  Parsing Act 1, Scene 3 … 4 characters, 131 lines
  Parsing Act 1, Scene 4 … 4 characters, 65 lines
  Parsing Act 1, Scene 5 … 2 characters, 82 lines
  Parsing Act 1, Scene 6 … 3 characters, 37 lines
  Parsing Act 1, Scene 7 … 2 characters, 99 lines
  Parsing Act 2, Scene 1 … 3 characters, 72 lines
  Parsing Act 2, Scene 2 … 2 characters, 91 lines
  Parsing Act 2, Scene 3 … 7 characters, 151 lines
  Parsing Act 2, Scene 4 … 2 characters, 54 lines
  Parsing Act 3, Scene 1 … 4 characters, 156 lines
  Parsing Act 3, Scene 2 … 2 characters, 62 lines
  Parsing Act 3, Scene 3 … 1 characters, 21 lines
  Parsing Act 3, Scene 4 … 4 characters, 168 lines
  Parsing Act 3, Scene 5 … 1 characters, 35 lines
  Parsing Act 3, Scene 6 … 1 characters, 62 lines
  Parsing Act 4, Scene 1 … 3 characters, 123 lines
  Parsing Act 4, Scene 2 … 2 characters, 94 lines
  Parsing Act 4, Scene 3 … 3 characters, 288 lines
  Parsing Act 5, Scene 1 … 1 characters, 47 lines
  Parsing Act 5, Scene 2 … 4 characters, 37 lines
  Parsing Act 5, Scene 3 … 2 characters, 71 lines
  Parsing Act 5, Scene 4 … 4 characters, 27 lines
  Parsing Act 5, Scene 5 … 2 characters, 57 lines
  Parsing Act 5, Scene 6 … 3 characters, 11 lines
  Parsing Act 5, Scene 7 … 5 characters, 35 lines
  Parsing Act 5, Scene 8 … 5 characters, 85 lines

════════════════════════════════════════════════════════════
  Character Network – Macbeth
════════════════════════════════════════════════════════════
  Nodes (characters) : 19
  Edges (co-scenes)  : 62

  Top 10 characters by lines spoken:
    MACBETH                          804 lines  (15 scenes)
    LADY MACBETH                     299 lines  (9 scenes)
    MALCOLM                          242 lines  (8 scenes)
    MACDUFF                          198 lines  (7 scenes)
    ROSS                             149 lines  (7 scenes)
    BANQUO                           138 lines  (7 scenes)
    LENNOX                           102 lines  (6 scenes)
    DUNCAN                            88 lines  (3 scenes)
    LADY MACDUFF                      74 lines  (1 scenes)
    HECATE                            44 lines  (2 scenes)

  Top 10 character pairings by shared-line weight:
    MACBETH                ↔  LADY MACBETH            weight=  664  (7 shared scene(s))
    MALCOLM                ↔  MACDUFF                 weight=  393  (6 shared scene(s))
    MACBETH                ↔  BANQUO                  weight=  386  (5 shared scene(s))
    LENNOX                 ↔  MACBETH                 weight=  289  (3 shared scene(s))
    MALCOLM                ↔  ROSS                    weight=  266  (3 shared scene(s))
    ROSS                   ↔  MACBETH                 weight=  227  (3 shared scene(s))
    ROSS                   ↔  MACDUFF                 weight=  215  (3 shared scene(s))
    MACBETH                ↔  MACDUFF                 weight=  155  (3 shared scene(s))
    MACBETH                ↔  ATTENDANT               weight=  132  (1 shared scene(s))
    MALCOLM                ↔  MACBETH                 weight=  130  (4 shared scene(s))

  Avg. shortest path (largest component): 1.725
  Graph density                          : 0.3626

► Scraping «Romeo and Juliet» …
  Found 26 scenes.
  Parsing Act 1, Scene 0 … 0 characters, 0 lines
  Parsing Act 1, Scene 1 … 11 characters, 238 lines
  Parsing Act 1, Scene 2 … 4 characters, 103 lines
  Parsing Act 1, Scene 3 … 2 characters, 110 lines
  Parsing Act 1, Scene 4 … 3 characters, 120 lines
  Parsing Act 1, Scene 5 … 5 characters, 147 lines
  Parsing Act 2, Scene 0 … 0 characters, 0 lines
  Parsing Act 2, Scene 1 … 3 characters, 45 lines
  Parsing Act 2, Scene 2 … 2 characters, 204 lines
  Parsing Act 2, Scene 3 … 2 characters, 97 lines
  Parsing Act 2, Scene 4 … 5 characters, 208 lines
  Parsing Act 2, Scene 5 … 1 characters, 80 lines
  Parsing Act 2, Scene 6 … 3 characters, 44 lines
  Parsing Act 3, Scene 1 … 7 characters, 203 lines
  Parsing Act 3, Scene 2 … 1 characters, 147 lines
  Parsing Act 3, Scene 3 … 2 characters, 179 lines
  Parsing Act 3, Scene 4 … 3 characters, 37 lines
  Parsing Act 3, Scene 5 … 4 characters, 262 lines
  Parsing Act 4, Scene 1 … 3 characters, 127 lines
  Parsing Act 4, Scene 2 … 3 characters, 48 lines
  Parsing Act 4, Scene 3 … 2 characters, 59 lines
  Parsing Act 4, Scene 4 … 2 characters, 31 lines
  Parsing Act 4, Scene 5 … 5 characters, 133 lines
  Parsing Act 5, Scene 1 … 2 characters, 90 lines
  Parsing Act 5, Scene 2 … 2 characters, 30 lines
  Parsing Act 5, Scene 3 … 10 characters, 321 lines

════════════════════════════════════════════════════════════
  Character Network – Romeo and Juliet
════════════════════════════════════════════════════════════
  Nodes (characters) : 20
  Edges (co-scenes)  : 111

  Top 10 characters by lines spoken:
    ROMEO                            671 lines  (14 scenes)
    JULIET                           668 lines  (11 scenes)
    FRIAR LAURENCE                   377 lines  (7 scenes)
    CAPULET                          302 lines  (9 scenes)
    MERCUTIO                         268 lines  (4 scenes)
    LADY CAPULET                     178 lines  (10 scenes)
    BENVOLIO                         165 lines  (7 scenes)
    PRINCE                            82 lines  (3 scenes)
    PARIS                             70 lines  (5 scenes)
    PETER                             65 lines  (2 scenes)

  Top 10 character pairings by shared-line weight:
    ROMEO                  ↔  JULIET                  weight=  548  (5 shared scene(s))
    ROMEO                  ↔  FRIAR LAURENCE          weight=  472  (4 shared scene(s))
    BENVOLIO               ↔  ROMEO                   weight=  448  (7 shared scene(s))
    CAPULET                ↔  ROMEO                   weight=  428  (5 shared scene(s))
    ROMEO                  ↔  MERCUTIO                weight=  412  (4 shared scene(s))
    LADY CAPULET           ↔  JULIET                  weight=  373  (5 shared scene(s))
    CAPULET                ↔  JULIET                  weight=  364  (4 shared scene(s))
    BENVOLIO               ↔  MERCUTIO                weight=  361  (4 shared scene(s))
    CAPULET                ↔  LADY CAPULET            weight=  275  (7 shared scene(s))
    PRINCE                 ↔  ROMEO                   weight=  267  (3 shared scene(s))

  Avg. shortest path (largest component): 1.458
  Graph density                          : 0.5842
@AnushaHR11 ➜ /workspaces/CSCE-5170-Graph-Theory (main) $ python3 shakespeare_mention_network.py --play othello

► Scraping «Othello» …
  Found 15 scenes.
                                                              
  Characters found: 12
  Alias patterns  : 43
                                                              
  Mention events  : 338

════════════════════════════════════════════════════════════
  Directed Mention Network – Othello
════════════════════════════════════════════════════════════
  Nodes (characters)  : 13
  Directed edges      : 69

  Top 10 characters by lines-in-speeches-that-mention-others:
    IAGO                            1188 lines  (out-degree 12)
    OTHELLO                          442 lines  (out-degree 8)
    DESDEMONA                        207 lines  (out-degree 6)
    CASSIO                           135 lines  (out-degree 6)
    LODOVICO                          84 lines  (out-degree 7)
    EMILIA                            82 lines  (out-degree 6)
    MONTANO                           63 lines  (out-degree 4)
    DUKE OF VENICE                    39 lines  (out-degree 4)
    BRABANTIO                         39 lines  (out-degree 4)
    RODERIGO                          38 lines  (out-degree 5)

  Top 10 most-mentioned characters (weighted in-degree):
    CASSIO                           629 weighted lines  (in-degree 8)
    OTHELLO                          551 weighted lines  (in-degree 11)
    DESDEMONA                        357 weighted lines  (in-degree 7)
    IAGO                             281 weighted lines  (in-degree 7)
    RODERIGO                         176 weighted lines  (in-degree 7)
    DUKE OF VENICE                   121 weighted lines  (in-degree 9)
    EMILIA                            74 weighted lines  (in-degree 3)
    MONTANO                           50 weighted lines  (in-degree 3)
    DUKE                              46 weighted lines  (in-degree 5)
    BIANCA                            35 weighted lines  (in-degree 2)

  Top 10 directed mention arcs (by weight):
    IAGO                   →  CASSIO                  weight=  406  mentions= 40
    IAGO                   →  OTHELLO                 weight=  337  mentions= 24
    OTHELLO                →  IAGO                    weight=  160  mentions= 29
    IAGO                   →  DESDEMONA               weight=  155  mentions= 11
    OTHELLO                →  DESDEMONA               weight=  140  mentions= 15
    IAGO                   →  RODERIGO                weight=  135  mentions= 15
    OTHELLO                →  CASSIO                  weight=   82  mentions= 17
    DESDEMONA              →  CASSIO                  weight=   72  mentions= 17
    IAGO                   →  DUKE OF VENICE          weight=   62  mentions=  6
    DESDEMONA              →  OTHELLO                 weight=   53  mentions=  9

  Reciprocal pairs     : 20 (58.0% of edges)
@AnushaHR11 ➜ /workspaces/CSCE-5170-Graph-Theory (main) $ python3 shakespeare_mention_network.py --play midsummer

► Scraping «A Midsummer Night's Dream» …
  Found 9 scenes.
                                                              
  Characters found: 22
  Alias patterns  : 43
                                                              
  Mention events  : 188

════════════════════════════════════════════════════════════
  Directed Mention Network – A Midsummer Night's Dream
════════════════════════════════════════════════════════════
  Nodes (characters)  : 21
  Directed edges      : 62

  Top 10 characters by lines-in-speeches-that-mention-others:
    HELENA                           266 lines  (out-degree 4)
    OBERON                           202 lines  (out-degree 7)
    LYSANDER                         186 lines  (out-degree 3)
    THESEUS                          170 lines  (out-degree 6)
    BOTTOM                           136 lines  (out-degree 8)
    PUCK                             124 lines  (out-degree 4)
    HERMIA                           120 lines  (out-degree 3)
    EGEUS                             99 lines  (out-degree 5)
    DEMETRIUS                         92 lines  (out-degree 4)
    TITANIA                           62 lines  (out-degree 6)

  Top 10 most-mentioned characters (weighted in-degree):
    HERMIA                           295 weighted lines  (in-degree 5)
    DEMETRIUS                        267 weighted lines  (in-degree 6)
    LYSANDER                         207 weighted lines  (in-degree 5)
    HELENA                           117 weighted lines  (in-degree 6)
    TITANIA                          115 weighted lines  (in-degree 2)
    THESEUS                           64 weighted lines  (in-degree 6)
    OBERON                            60 weighted lines  (in-degree 2)
    HIPPOLYTA                         49 weighted lines  (in-degree 3)
    PUCK                              40 weighted lines  (in-degree 1)
    SNOUT                             32 weighted lines  (in-degree 3)

  Top 10 directed mention arcs (by weight):
    HELENA                 →  HERMIA                  weight=  120  mentions=  8
    HELENA                 →  DEMETRIUS               weight=  113  mentions= 11
    HERMIA                 →  LYSANDER                weight=   99  mentions= 16
    OBERON                 →  TITANIA                 weight=   84  mentions=  8
    LYSANDER               →  HERMIA                  weight=   78  mentions= 10
    LYSANDER               →  HELENA                  weight=   68  mentions= 12
    PUCK                   →  OBERON                  weight=   56  mentions=  4
    THESEUS                →  HERMIA                  weight=   42  mentions=  4
    THESEUS                →  HIPPOLYTA               weight=   41  mentions=  4
    OBERON                 →  PUCK                    weight=   40  mentions=  2

  Reciprocal pairs     : 17 (54.8% of edges)
