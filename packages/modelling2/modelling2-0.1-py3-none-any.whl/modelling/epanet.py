from modelling import *

def write_inp(outpath, scenarioid, database='dev'):
    # Heading to write for the inp
    epanet_headings = {
        '[TITLE]': [],
        '[JUNCTIONS]': [';ID', 'Elev', 'Demand', 'Pattern'],
        '[RESERVOIRS]': [';ID', 'Head', 'Pattern'],
        '[TANKS]': [';ID', 'Elevation', 'InitLevel', 'MinLevel', 'MaxLevel', 'Diameter', 'MinVol', 'VolCurve'],
        '[PIPES]': [';ID', 'Node1', 'Node2', 'Length', 'Diameter', 'Roughness', 'MinorLoss', 'Status'],
        '[PUMPS]': [';ID', 'Node1', 'Node2', 'Parameters'],
        '[VALVES]': [';ID', 'Node1', 'Node2', 'Diameter', 'Type', 'Setting', 'MinorLoss'],
        '[TAGS]': [],
        '[DEMANDS]': [';Junction', 'Demand', 'Pattern', 'Category'],
        '[STATUS]': [';ID', 'Status/Setting'],
        '[PATTERNS]': [';ID', 'Multipliers'],
        '[CURVES]': [';ID', 'X-Value', 'Y-Value'],
        '[CONTROLS]': [],
        '[RULES]': [],
        '[ENERGY]': [],
        '[EMITTERS]': [';Junction', 'Coefficient'],
        '[QUALITY]': [';Node', 'InitQual'],
        '[SOURCES]': [';Node', 'Type', 'Quality', 'Pattern'],
        '[REACTIONS]': [],
        '[MIXING]': [';Tank', 'Model'],
        '[TIMES]': [],
        '[REPORT]': [],
        '[OPTIONS]': [],
        '[COORDINATES]': [';Node', 'X-Coord', 'Y-Coord'],
        '[VERTICES]': [';Link', 'X-Coord', 'Y-Coord'],
        '[LABELS]': [';X-Coord ', 'Y-Coord ', 'Label & Anchor Node'],
        '[BACKDROP]': [],
        '[END]': []
    }

    # Key words for epanet database queries
    epanet_query = {
        '[JUNCTIONS]': 'junctions',
        '[RESERVOIRS]': 'reservoirs',
        '[TANKS]': 'tanks',
        '[PIPES]': 'pipes',
        '[PUMPS]': 'pumps',
        '[VALVES]': 'valves',
        '[DEMANDS]': 'demands',
        '[STATUS]': 'status',
        '[PATTERNS]': 'patterns',
        '[CURVES]': 'curves',
        '[RULES]': 'rules',
        '[COORDINATES]': 'coordinates',
        '[VERTICES]': 'vertices'
    }

    with open(outpath, 'w') as outfile:
        for sec, headings in epanet_headings.items():
            print('Writing {}...'.format(sec))
            outfile.write(sec + '\n')
            outfile.write('\t'.join(headings) + '\n' if len(headings) > 0 else '')
            query = None

            if sec == '[TITLE]':
                outfile.write('Scenario {}\n'.format(scenarioid))
            elif sec == '[RULES]':
                query = '''
                select 
                    'RULE' || ' ' || 
                    r.name || chr(10) || 
                    string_agg(
                        coalesce((g.grc).statement, '') || ' ' || 
                        coalesce((g.grc).objectvariable, '') || ' ' || 
                        coalesce((g.grc).attributevariable, '') || ' ' || 
                        coalesce((g.grc).operator, '') || ' ' || 
                        coalesce((g.grc).value, ''), 
                        chr(10) order by (g.grc).ruleid, (g.grc).sequence asc
                    ) || chr(10) || 
                    'PRIORITY' || ' ' || 
                    r.priority as "rules"
                from (
                    select modelling.epanet_getrulecomponents(array_agg(gr.ruleid)) grc from (
                        select ruleid from modelling.epanet_getrules({0}, 1) gr1
                        union 
                        select ruleid from modelling.epanet_getrules({0}, 2) gr2
                    ) gr
                ) g
                join modelling.rule r on 
                    (g.grc).ruleid = r.ruleid and r.ismodelled
                where r.ismodelled and r.ruletypeid=1
                group by (g.grc).ruleid, r.ruletypeid, r.name, r.priority;'''.format(scenarioid)
            elif sec == '[CONTROLS]':
                query = '''
                select trim(regexp_replace(controls, '\s+', ' ', 'g')) as controls from (
                    select 
                        string_agg(
                            coalesce((g.grc).statement, '') || ' ' || 
                            coalesce((g.grc).objectvariable, '') || ' ' || 
                            coalesce((g.grc).attributevariable, '') || ' ' || 
                            coalesce((g.grc).operator, '') || ' ' || 
                            coalesce((g.grc).value, ''), 
                            ' ' order by (g.grc).ruleid, (g.grc).sequence asc
                        )  as "controls"
                    from (
                        select modelling.epanet_getrulecomponents(array_agg(gr.ruleid)) grc from (
                            select ruleid from modelling.epanet_getrules({0}, 1) gr1
                            union 
                            select ruleid from modelling.epanet_getrules({0}, 2) gr2
                        ) gr
                    ) g
                    join modelling.rule r on 
                        (g.grc).ruleid = r.ruleid and r.ismodelled
                    where r.ismodelled and r.ruletypeid=2
                    group by (g.grc).ruleid, r.ruletypeid, r.priority
                    union 
                    select gcp.control as controls from modelling.epanet_getcontrolfrompattern({0}) gcp
                ) c
                order by controls;'''.format(scenarioid)
            elif sec == '[ENERGY]':
                outfile.write(
                    "Global EFFIC\t70.000000\n" \
                    "Global Price\t0\n" \
                    "Demand Charge\t0.000000\n")
            elif sec == '[REACTIONS]':
                query = '''
                    with temp_reactions (modelrunoptiontypeid, name, value) as (
                        values 
                        (45, 'Order Bulk', '1'),
                        (46, 'Order Tank', '1'),
                        (47, 'Order Wall', '1'),
                        (48, 'Global Bulk', '0'),
                        (49, 'Global Wall', '0'),
                        (50, 'Limiting Potential', '0'),
                        (51, 'Roughness Correlation', '0')
                    )
                    select
                        tr.name,
                        case 
                            when m.value is null then tr.value
                            else m.value
                        end
                    from temp_reactions tr
                    left join (
                        select 
                            mrot.modelrunoptiontypeid, mro.value
                        from modelling.modelrunoption mro
                        join modelling.scenario s on 
                            s.modelrunoptionsetid=mro.modelrunoptionsetid and s.scenarioid={0}
                        join modelling.modelrunoptiontype mrot on 
                            mro.modelrunoptiontypeid=mrot.modelrunoptiontypeid
                        where mrot.modelrunoptiontypeid in (45, 46, 47, 48, 49, 50, 51)
                    ) m on m.modelrunoptiontypeid=tr.modelrunoptiontypeid;'''.format(scenarioid)
            elif sec == '[OPTIONS]':
                query = '''
                    with temp_options (modelrunoptiontypeid, name, value) as (
                        values 
                        (52, 'Tolerance', '0.001'),
                        (30, 'Diffusivity', '1.00187'),
                        (31, 'Quality', 'None'),
                        (32, 'Emitter Exponent', '1.0'),
                        (33, 'Demand Multiplier', '1.0'),
                        (34, 'Pattern', '1'),
                        (35, 'Unbalanced', 'Continue 10'),
                        (36, 'DAMPLIMIT', '0'),
                        (37, 'MAXCHECK', '10'),
                        (38, 'CHECKFREQ', '2'),
                        (39, 'Accuracy', '0.001'),
                        (40, 'Trials', '80'),
                        (41, 'Viscosity', '0.978537'),
                        (42, 'Specific Gravity', '1.0'),
                        (29, 'Headloss', 'H-W'),
                        (44, 'Units', 'LPS')
                    )
                    select
                        tt.name,
                        case 
                            when m.value is null then tt.value
                            else m.value
                        end
                    from temp_options tt
                    left join (
                        select 
                            mrot.modelrunoptiontypeid, mro.value
                        from modelling.modelrunoption mro
                        join modelling.scenario s on 
                            s.modelrunoptionsetid=mro.modelrunoptionsetid and s.scenarioid={0}
                        join modelling.modelrunoptiontype mrot on 
                            mro.modelrunoptiontypeid=mrot.modelrunoptiontypeid
                        where mrot.modelrunoptiontypeid in (52,30,31,32,33,34,35,36,37,38,39,40,41,42,29,44)
                    ) m on m.modelrunoptiontypeid=tt.modelrunoptiontypeid;'''.format(scenarioid)
            elif sec == '[TIMES]':
                query = '''
                    with temp_times (modelrunoptiontypeid, name, value) as (
                        values 
                        (9, 'Duration', '24:00'),
                        (10, 'Hydraulic Timestep', '00:05'),
                        (-1, 'Quality Timestep', '00:05'),
                        (11, 'Pattern Timestep', '00:05'),
                        (12, 'Pattern Start', '00:00'),
                        (-1, 'Report Timestep', '00:05'),
                        (13, 'Report Start', '00:00'),
                        (14, 'Start ClockTime', '12 am'),
                        (15, 'STATISTIC', 'NONE')
                    )
                    select
                        tt.name,
                        case 
                            when m.value is null then tt.value
                            when m.modelrunoptiontypeid = 9 then TO_CHAR((m.value || ' hour')::interval, 'HH24:MI')
                            when m.modelrunoptiontypeid in (10, 11) then TO_CHAR((m.value || ' millisecond')::interval, 'HH24:MI')
                            when m.modelrunoptiontypeid in (12, 13) then TO_CHAR((m.value || ' second')::interval, 'HH24:MI')
                            else m.value
                        end
                    from temp_times tt
                    left join (
                        select 
                            mrot.modelrunoptiontypeid, mro.value
                        from modelling.modelrunoption mro
                        join modelling.scenario s on 
                            s.modelrunoptionsetid=mro.modelrunoptionsetid and s.scenarioid={0}
                        join modelling.modelrunoptiontype mrot on 
                            mro.modelrunoptiontypeid=mrot.modelrunoptiontypeid
                        where mrot.modelrunoptiontypeid in (9, 10, 11, 12, 13, 14, 15)
                    ) m on m.modelrunoptiontypeid=tt.modelrunoptiontypeid;'''.format(scenarioid)
            elif sec == '[REPORT]':
                outfile.write(
                    "Status\tYes\n" \
                    "Summary\tNo\n" \
                    "Page\t0")
            elif sec in epanet_query.keys():
                query = 'select * from modelling.epanet_get{}({});'.format(epanet_query[sec], scenarioid)

            if query is not None:
                df = db.read_df(query, database=database)
                outfile.write(df.to_csv(header=False, index=False).replace(',', '\t').replace('\r', '').replace('"', ''))

            outfile.write('\n')

