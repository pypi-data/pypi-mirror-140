import pandas as pd
import geopandas as gp
import networkx as nx
import matplotlib.pyplot as plt
from collections import OrderedDict
from shapely.geometry import Point, LineString, Polygon, LinearRing
from shapely import affinity
from shapely.ops import split, unary_union, nearest_points
import numpy as np
import shlex


class ETABS:
    def __init__(self, file):
        self.allpoints = gp.GeoDataFrame(columns=['name', 'x', 'y', 'z', 'dx', 'dy', 'geometry']).set_index('name')
        self.alllines = gp.GeoDataFrame(columns=['name', 'linetype', 'p1', 'p2', 'geometry']).set_index('name')
        self.alllinks = gp.GeoDataFrame(columns=['name', 'level', 'p1', 'p2', 'geometry']).set_index('name')
        self.allareas = gp.GeoDataFrame(columns=['name', 'areatype', 'p1', 'p2', 'p3', 'p4', 'geometry']).set_index('name')

        self.lineassigns = gp.GeoDataFrame(columns=['name', 'level', 'section', 'angle']).set_index('name')
        self.linkassigns = gp.GeoDataFrame(columns=['name', 'property']).set_index('name')
        self.areaassigns = gp.GeoDataFrame(columns=['name', 'level', 'section']).set_index('name')

        self.sections = pd.DataFrame(columns=['name', 'material', 'shape', 'D', 'B']).set_index('name')
        self.areaprop = pd.DataFrame(columns=['name', 'material', 'proptype', 'type', 'platetype', 'TM', 'TB']).set_index('name')
        self.stories = pd.DataFrame(columns=['name', 'height', 'total_height']).set_index('name')
        self.materials = pd.DataFrame(columns=['name', 'M', 'W', 'type', 'E', 'U', 'A']).set_index('name')

        self.grid = pd.DataFrame(columns=['label', 'xa', 'ya', 'xb', 'yb', 'geometry'])
        self.gridpoints = gp.GeoDataFrame(columns=['name', 'geometry'])

        self.story = None
        self.points = None
        self.lines = None
        self.links = None
        self.areas = None
        self.core = (36000, -68000, 69000, -42000)

        self._filelines = None
        self.subnetworks = None
        self.reade2k(file)

    ####################################################################################################################
    # Read .e2k file
    ####################################################################################################################
    def reade2k(self, file):
        with open(file, 'r') as f:
            self._filelines = f.readlines()

        self._getheadings()
        self._reade2k_points()

        self._reade2k_sections()
        self._reade2k_areaproperties()
        self._reade2k_stories()
        self._reade2k_materials()

        self._reade2k_lines()
        self._reade2k_lineassign()

        self._reade2k_areas()
        self._reade2k_areaassign()

        self._reade2k_links()
        self._reade2k_linkassign()

        self._reade2k_grid()
        self._creategridpoints()

    def _getheadings(self):
        self._headings = OrderedDict()
        for line in self._filelines:
            line_split = line.split(' ')

            if line_split[0] == '$':
                heading = ' '.join(line_split[1:]).replace('\n', '')
                self._headings[heading] = self._filelines.index(line)

    def _nextheading(self, key):
        keys = list(self._headings.keys())
        for i in range(len(keys)):
            h = keys[i]
            if h == key:
                if i < len(keys) - 1:
                    return keys[i + 1]
                else:
                    return None

        print('{} does not exist'.format(key))

    def _getheadinglines(self, heading):
        if heading not in list(self._headings.keys()):
            return []

        next_heading = self._nextheading(heading)

        start_idx = self._headings[heading]
        end_idx = self._headings[next_heading] if next_heading is not None else len(self._filelines)
        return self._filelines[start_idx + 1:end_idx]

    def _reade2kfilelines(self, heading, columns=None, skip=1):
        lines = self._getheadinglines(heading)

        all_list = []
        for l in lines:
            line = shlex.split(l)
            line = list(filter(None, line))[skip:]

            if columns is not None:
                l_list = []
                for col in columns:
                    if col < len(line):
                        l_list.append(line[col].replace('\n', ''))
            else:
                l_list = [l.replace('\n', '') for l in line]

            if l_list != []:
                all_list.append(l_list)

        return all_list

    def _reade2k_points(self):
        pt_list = self._reade2kfilelines('POINT COORDINATES', [0, 1, 2, 3])
        for i in range(len(pt_list)):
            if len(pt_list[i]) < 2:
                pt_list.pop(i)
                continue

            if len(pt_list[i]) == 3:
                pt_list[i].append('0')

            pt_list[i][3] = '0' if pt_list[i][3] == '' else pt_list[i][3]
            pt_list[i].append(Point(float(pt_list[i][1]), float(pt_list[i][2])))

        self.allpoints = self.allpoints.append(gp.GeoDataFrame(pt_list, columns=['name', 'x', 'y', 'z', 'geometry']))
        self.allpoints = self.allpoints.set_geometry('geometry')
        self.allpoints = self.allpoints.set_index('name')
        self.allpoints['dx'] = 0
        self.allpoints['dy'] = 0

    def _reade2k_lines(self):
        ln_list = self._reade2kfilelines('LINE CONNECTIVITIES', [0, 1, 2, 3])

        for i in range(len(ln_list)):
            if len(ln_list[i]) < 4:
                ln_list.pop(i)
                continue

            p1 = ln_list[i][2]
            p2 = ln_list[i][3]
            geom = LineString([self.allpoints.loc[p1, 'geometry'], self.allpoints.loc[p2, 'geometry']])

            ln_list[i].append(geom)

        self.alllines = self.alllines.append(
            gp.GeoDataFrame(ln_list, columns=['name', 'linetype', 'p1', 'p2', 'geometry']), sort=False)
        self.alllines = self.alllines.set_geometry('geometry')
        self.alllines = self.alllines.set_index('name')

    def _reade2k_links(self):
        ln_list = self._reade2kfilelines('LINK CONNECTIVITIES', [0, 2, 3, 6])

        for i in range(len(ln_list)):
            if len(ln_list[i]) < 4:
                ln_list.pop(i)
                continue

            p1 = ln_list[i][2]
            p2 = ln_list[i][3]
            geom = LineString([self.allpoints.loc[p1, 'geometry'], self.allpoints.loc[p2, 'geometry']])

            ln_list[i].append(geom)

        self.alllinks = self.alllinks.append(
            gp.GeoDataFrame(ln_list, columns=['name', 'level', 'p1', 'p2', 'geometry']), sort=False)
        self.alllinks = self.alllinks.set_geometry('geometry')
        self.alllinks = self.alllinks.set_index('name')

    def _reade2k_areas(self):
        ln_list = self._reade2kfilelines('AREA CONNECTIVITIES', [0, 1, 3, 4, 5, 6])

        for i in range(len(ln_list)):
            if len(ln_list[i]) < 4:
                ln_list.pop(i)
                continue

            p1 = ln_list[i][2]
            p2 = ln_list[i][3]
            geom = LineString([self.allpoints.loc[p1, 'geometry'], self.allpoints.loc[p2, 'geometry']])

            ln_list[i].append(geom)

        self.allareas = self.allareas.append(
            gp.GeoDataFrame(ln_list, columns=['name', 'areatype', 'p1', 'p2', 'p3', 'p4', 'geometry']), sort=False)
        self.allareas = self.allareas.set_geometry('geometry')
        self.allareas = self.allareas.set_index('name')

    def _reade2k_grid(self):
        gd_heading = 'GRIDS'
        gd_lines = self._reade2kfilelines(gd_heading, skip=0)

        gd_list = []
        gridline_headings = ['XA', 'YA', 'XB', 'YB']

        for gd_line in gd_lines:
            row_list = []

            if 'GENGRID' in gd_line and 'LABEL' in gd_line:
                name_idx = gd_line.index('LABEL') + 1
                row_list.append(gd_line[name_idx])

                for gd_head in gridline_headings:
                    idx = gd_line.index(gd_head) + 1
                    row_list.append(float(gd_line[idx]))

                geom = LineString([Point(row_list[1], row_list[2]), Point(row_list[3], row_list[4])])
                row_list.append(geom)
                gd_list.append(row_list)
            else:
                continue

        self.grid = self.grid.append(pd.DataFrame(gd_list, columns=['label', 'xa', 'ya', 'xb', 'yb', 'geometry']))
        self.grid = self.grid.set_geometry('geometry')

    def _creategridpoints(self):
        x = pd.concat([self.grid['xa'], self.grid['xb']])
        y = pd.concat([self.grid['ya'], self.grid['yb']])

        x = x.sort_values().unique()
        y = y.sort_values().unique()

        gd_list = []
        for i in range(len(x)):
            for j in range(len(y)):
                row = str(i + 1)
                col = self._numtostring(j + 1)
                name = row + col
                pt = Point(x[i], y[j])
                gd_list.append([name, row, col, pt])

        self.gridpoints = self.gridpoints.append(pd.DataFrame(gd_list, columns=['name', 'row', 'col', 'geometry']),
                                                 sort=False)
        self.gridpoints = self.gridpoints.set_geometry('geometry')
        self.gridpoints = self.gridpoints.set_index('name')

    def _reade2k_lineassign(self):
        ln_list = self._reade2kfilelines('LINE ASSIGNS', [0, 1, 3, 5])

        self.lineassigns = gp.GeoDataFrame(ln_list, columns=['name', 'level', 'section', 'angle'])
        self.lineassigns = self.lineassigns.set_index(['level', 'name']).sort_index()

    def _reade2k_linkassign(self):
        ln_list = self._reade2kfilelines('LINK ASSIGNS', [0, 2])

        self.linkassigns = gp.GeoDataFrame(ln_list, columns=['name', 'property'])
        self.linkassigns = self.linkassigns.set_index(['name']).sort_index()

    def _reade2k_areaassign(self):
        ln_list = self._reade2kfilelines('AREA ASSIGNS', [0, 1, 3])

        self.areaassigns = gp.GeoDataFrame(ln_list, columns=['name', 'level', 'section'])
        self.areaassigns = self.areaassigns.set_index(['level', 'name']).sort_index()

    def _reade2k_sections(self):
        ln_list = self._reade2kfilelines('FRAME SECTIONS', [0, 2, 4, 6, 8])

        self.sections = self.sections.append(pd.DataFrame(ln_list, columns=['name', 'material', 'shape', 'D', 'B']),
                                             sort=False)
        self.sections = self.sections.drop_duplicates(subset='name')
        self.sections = self.sections.set_index('name')

    def _reade2k_stories(self):
        ln_list = self._reade2kfilelines('STORIES', [0, 2])

        self.stories = self.stories.append(pd.DataFrame(ln_list, columns=['name', 'height']), sort=False)

        if not self.stories.empty:
            self.stories['total_height'] = self.stories.loc[::-1, 'height'].astype('int').cumsum()[::-1]
            self.stories['total_height'] = self.stories.total_height - self.stories.total_height.iloc[-1]

    def _reade2k_materials(self):
        ln_list = self._reade2kfilelines('MATERIAL PROPERTIES', [0, 2, 4, 6, 8, 10, 12])
        ln_list = ln_list[::2]

        self.materials = self.materials.append(pd.DataFrame(ln_list, columns=['name', 'M', 'W', 'type', 'E', 'U', 'A']),
                                               sort=False)
        self.materials = self.materials.set_index('name')

    def _reade2k_areaproperties(self):
        ln_list = self._reade2kfilelines('WALL/SLAB/DECK PROPERTIES', [0, 2, 4, 6, 8, 10, 12])

        self.areaprop = self.areaprop.append(
            pd.DataFrame(ln_list, columns=['name', 'material', 'proptype', 'type', 'platetype', 'TM', 'TB']),
            sort=False)
        self.areaprop = self.areaprop.set_index('name')

    def _reade2k_linkproperties(self):
        ln_list = self._reade2kfilelines('LINK PROPERTIES')

        linkprop = pd.DataFrame(columns=['name', 'type', 'u1', 'u2', 'u3', 'r1', 'r2', 'r3'])
        for line in ln_list:
            if len(linkprop.name.contains(line[0])) == 0:
                linkprop = linkprop.append(pd.DataFrame([line[0]], columns=['name']))

            for i in range(len(line)):
                if line[i].lower() in linkprop.columns:
                    linkprop.loc[linkprop.name == line[0], line[i].lower()] = line[i + 1]

        self.linkprop = linkprop
        self.linkprop = self.linkprop.set_index('name')

    def _getstorylines(self):
        if self.story not in self.lineassigns.index.get_level_values(0):
            return gp.GeoDataFrame(columns=['linetype', 'p1', 'p2', 'geometry'])

        lines = self.lineassigns.loc[self.story, :].copy()
        for col in ['linetype', 'p1', 'p2', 'geometry']:
            lines[col] = None

        if not lines.empty:
            for col in ['linetype', 'p1', 'p2', 'geometry']:
                lines[col] = self.alllines[col]
            lines = lines.set_geometry('geometry')
        return lines

    def _getstorylinks(self):
        if self.story not in self.alllinks.level:
            return gp.GeoDataFrame(columns=['level', 'p1', 'p2', 'geometry'])

        links = self.alllinks.loc[self.alllinks.level == self.story, :].copy()
        if not links.empty:
            links['property'] = self.linkassigns['property']
            links = links.set_geometry('geometry')
        return links

    def _getstoryareas(self):
        if self.story not in self.areaassigns.index.get_level_values(0):
            return gp.GeoDataFrame(columns=['areatype', 'p1', 'p2', 'p3', 'p4', 'geometry'])

        areas = self.areaassigns.loc[self.story, :].copy()
        for col in ['areatype', 'p1', 'p2', 'p3', 'p4', 'geometry']:
            areas[col] = None

        if not areas.empty:
            for col in ['areatype', 'p1', 'p2', 'p3', 'p4', 'geometry']:
                areas[col] = self.allareas[col]
            areas = areas.set_geometry('geometry')
        return areas

    def _getpoints(self, lines, areas):
        ptnames = []
        if not lines.empty:
            ptnames.extend(list(lines.p1))
            ptnames.extend(list(lines.p2))

        if not areas.empty:
            ptnames.extend(list(areas.p1))
            ptnames.extend(list(areas.p2))
            ptnames.extend(list(areas.p3))
            ptnames.extend(list(areas.p4))

        ptnames = list(set(ptnames))
        points = self.allpoints.loc[ptnames, :].copy()
        # height = self.stories.loc[self.stories.name == self.story, 'total_height'].values[0]
        # points.geometry = points.apply(lambda row: Point(float(row.x), float(row.y), height + float(row.z)), axis=1)
        return points

    def _getstory(self, story):
        self.story = story
        self.points = gp.GeoDataFrame()
        self.lines = self._getstorylines()
        self.links = self._getstorylinks()
        self.areas = self._getstoryareas()

        if (not self.lines.empty) or (not self.areas.empty):
            self.points = self._getpoints(self.lines, self.areas)
            self.points['lockedx'] = False
            self.points['lockedy'] = False
            self._createpointsections()

    ####################################################################################################################
    # Snapping
    ####################################################################################################################
    def snap(self, story):
        print('Getting story and creating point sections...')
        self._getstory(story)

        if not self.points.empty:
            # print('Extending lines in column...')
            # self._extendisolatedlinesincolumn()
            # self._createpointsections()

            # print('Connect touching columns...')
            # self._connecttouchingcolumns()

            print('Splitting lines...')
            self._splitlinesbypoints()
            # self._splitareasbypoints()

            print('Snapping lines...')
            self._snaplinestopoints()
            # self._snapareastopoints()

            print('Snapping points outside core to grid intersections...')
            self._snappointstogridpoints()

            print('Snapping points outside core to gridlines...')
            self._snappointstogridlines()

            print('Snapping points outside core to columns...')
            self._snaptocolumns()

            # print('Snapping isolated points to largest section...')
            # self._snapisolatedendpoints()

            # print('Snapping points to largest section...')
            # self._snaptolargestpoints()

            print('Aligning networks...')
            self._alignnetworks()

            # print('Removing and reassigning duplicate points...')
            # self._removeduplicatepoints()

            print('Creating rigid links in core...')
            self._connectcolumnstolines()

            print('Updating geometry...')
            self._updateallgeometry()

        print('Story ' + self.story + ' Complete')

    # def _createrigidlinks(self):
        # self._movepointstocolumnedge()
        # self._connectcolumnstolines()
        # self._splitlinesbypoints()
        # self._splitareasbypoints()
        # self._snaplinestopoints()
        # self._snapareastopoints()
        # self._snapisolatedendpoints()
        # self._updategeometry()
        # self._removeduplicatepoints()

    @staticmethod
    def _getclosegeometry(geom1, geom2):
        possible_matches_index = list(geom1.sindex.intersection(geom2.bounds))
        return geom1.iloc[possible_matches_index]

    @staticmethod
    def _getclosestpoint(closepts, pt):
        dist = closepts.geometry.distance(pt.geometry)
        return closepts.loc[dist.idxmin(), 'geometry']

    @staticmethod
    def _snaptoline(closeline, pt):
        return closeline.interpolate(closeline.project(pt))

    @staticmethod
    def _getdirection(pt, newpt):
        distx = abs(pt.x - newpt.x)
        disty = abs(pt.y - newpt.y)

        if distx > disty:
            return 'x'
        else:
            return 'y'

    def columns(self):
        if self.points.empty:
            return gp.GeoDataFrame()
        return self.points[self.points.pointtype == 'COLUMN']

    def notcolumns(self):
        if self.points.empty:
            return gp.GeoDataFrame()
        return self.points[self.points.pointtype != 'COLUMN']

    def incore(self, geom):
        if geom.empty:
            return gp.GeoDataFrame()
        possible_matches_index = list(geom.sindex.intersection(self.core))
        return geom.iloc[possible_matches_index]

    def not_incore(self, geom):
        if geom.empty:
            return gp.GeoDataFrame()
        possible_matches_index = list(geom.sindex.intersection(self.core))
        return geom[~geom.index.isin(geom.iloc[possible_matches_index].index)]

    def _lineswithpoints(self, ptnames):
        return self.lines.loc[self.lines.p1.isin(ptnames) | self.lines.p2.isin(ptnames), :]

    def _areaswithpoints(self, ptnames):
        return self.areas.loc[self.areas.p1.isin(ptnames) | self.areas.p2.isin(ptnames) | self.areas.p3.isin(
            ptnames) | self.areas.p4.isin(ptnames), :]

    def _getlinesandareas(self):
        return pd.concat([self.lines, self.areas], sort=False)

    def _connecttouchingcolumns(self):
        columns = self.columns().set_geometry('polygon')

        p1 = []
        p2 = []
        for i, pt in columns.iterrows():
            connectedpts = self._connectedpointstolines(pt)
            touchingcolumns = self._getclosegeometry(columns[~columns.index.isin(pt.index)], pt['polygon'])

            for col in touchingcolumns.index:
                if col not in connectedpts:
                    p1.append(pt.name)
                    p2.append(col)

        self._createrigidlinkfrompoints(p1, p2)

    def _snappointstogridpoints(self):
        columnsincore = self.incore(self.columns())

        for i, pt in self.points.iterrows():
            if pt.name in columnsincore.index:
                continue

            closegridpts = self._getclosegeometry(self.gridpoints, pt['polygon'])
            closegridpts = closegridpts[closegridpts.within(pt['polygon'])]
            if not closegridpts.empty:
                closestgridpt = self._getclosestpoint(closegridpts, pt)
                self.points.loc[i, 'geometry'] = closestgridpt
                self.points.loc[i, 'lockedx'] = True
                self.points.loc[i, 'lockedy'] = True

    def _snappointstogridlines(self):
        columnsincore = self.incore(self.columns())

        for i, pt in self.points.iterrows():
            if pt.name in columnsincore.index:
                continue

            closegridlines = self._getclosegeometry(self.grid, pt.polygon)
            closegridlines = closegridlines[closegridlines.intersects(pt.polygon)]
            if not closegridlines.empty:
                for gridline in closegridlines.geometry:
                    newpt = self._snaptoline(gridline, pt['geometry'])
                    self.points.loc[i, 'geometry'] = newpt
                    snapdir = self._getdirection(pt.geometry, newpt)
                    if snapdir == 'x':
                        self.points.loc[i, 'lockedx'] = True
                    else:
                        self.points.loc[i, 'lockedy'] = True
                    pt.geometry = newpt

    def _connectedpointstolines(self, pt):
        ptnames = []
        ptnames.extend(list(self.lines.loc[self.lines.p1 == pt.name, 'p2'].values))
        ptnames.extend(list(self.lines.loc[self.lines.p2 == pt.name, 'p1'].values))
        ptnames = [ptname for ptname in ptnames if ptname != pt.name]
        return ptnames

    def _connectedpointstoareas(self, pt):
        ptnames = []
        ptnames.extend(list(self.areas.loc[self.areas.p1 == pt.name, 'p2'].values))
        ptnames.extend(list(self.areas.loc[self.areas.p2 == pt.name, 'p1'].values))
        ptnames = [ptname for ptname in ptnames if ptname != pt.name]
        return ptnames

    def _alignwithconnectedpoints(self, pt):
        connectedptnames = self._connectedpointstolines(pt)
        alignpts = self.points.loc[connectedptnames, :]

        coords = list(pt.geometry.coords[0])
        for i, alignpt in alignpts.iterrows():
            distx = abs(pt.geometry.x - alignpt.geometry.x)
            disty = abs(pt.geometry.y - alignpt.geometry.y)
            if distx < disty:
                coords[0] = alignpt.geometry.x
            elif distx > disty:
                coords[1] = alignpt.geometry.y

        return Point(coords)

    def _alignconnectedpoints(self, pt):
        connectedptnames = self._connectedpointstolines(pt)
        alignpts = self.points.loc[connectedptnames, :]

        for i, alignpt in alignpts.iterrows():
            coords = list(alignpt.geometry.coords[0])

            distx = abs(pt.geometry.x - alignpt.geometry.x)
            disty = abs(pt.geometry.y - alignpt.geometry.y)
            if (distx < disty) and not alignpt.lockedx and pt.lockedx:
                coords[0] = pt.geometry.x
                self.points.loc[i, 'lockedx'] = True
            elif (distx > disty) and not alignpt.lockedy and pt.lockedy:
                coords[1] = pt.geometry.y
                self.points.loc[i, 'lockedy'] = True

            self.points.loc[i, 'geometry'] = Point(coords)

    def _findlockednode(self, nodenames):
        nodes = self.points.loc[nodenames, :]
        lockednodenames = list(nodes[nodes['lockedx'] & nodes['lockedy']].index)
        if len(lockednodenames) > 0:
            return lockednodenames[0]

        lockednodenames = list(nodes[nodes['lockedx'] | nodes['lockedy']].index)
        if len(lockednodenames) > 0:
            return lockednodenames[0]
        else:
            return None

    def _alignsubnetwork(self, nodenames):
        nodeset = set(nodenames)
        while len(nodeset) > 0:
            lockednode = self._findlockednode(list(nodeset))
            if lockednode is not None:
                pt = self.points.loc[lockednode, :]
                self._alignconnectedpoints(pt)
                nodeset.remove(lockednode)
            else:
                break

    def _getsubnetworks(self):
        graph = nx.from_pandas_edgelist(self.lines, 'p1', 'p2')

        all_nodes = set(graph.nodes)
        cols = ['nodes', 'num_nodes', 'edges', 'num_edges']
        subnetworks = pd.DataFrame(columns=cols)

        while len(all_nodes) > 0:
            for rand_node in all_nodes:
                break

            tree = nx.algorithms.bfs_tree(graph, rand_node)

            ids_from_nodes = set([node for node in tree.nodes])
            ids_from_edges = set([edge for edge in tree.edges])

            subnetworks = subnetworks.append(
                pd.Series([list(ids_from_nodes), len(ids_from_nodes), list(ids_from_edges), len(ids_from_edges)],
                          index=cols), ignore_index=True)
            all_nodes.difference_update(ids_from_nodes)

        self.subnetworks = subnetworks

    def _alignnetworks(self):
        self._getsubnetworks()
        for i, row in self.subnetworks.iterrows():
            self._alignsubnetwork(row.nodes)
        self._updategeometry()

    def _removeduplicatepoints(self):
        for i, pt in self.points.iterrows():
            if pt.name in self.points.index:
                duplicatepts = self.points[
                    (self.points.geometry.geom_almost_equals(pt.geometry, decimal=3)) & (self.points.index != pt.name)]
                if not duplicatepts.empty:
                    if all(duplicatepts.pointtype != 'COLUMN') and all(
                            duplicatepts.set_geometry('polygon').polygon.area <= pt.polygon.area):
                        for col in ['p1', 'p2']:
                            self.lines.loc[self.lines[col].isin(duplicatepts.index), col] = pt.name
                        for col in ['p1', 'p2', 'p3', 'p4']:
                            self.areas.loc[self.areas[col].isin(duplicatepts.index), col] = pt.name

                        self.points = self.points.drop(duplicatepts.index)

        self._updategeometry()

    def _removeallduplicatepoints(self):
        for i, pt in self.allpoints.iterrows():
            if pt.name in self.allpoints.index:
                duplicatepts = self.allpoints[
                    (self.allpoints.geometry.geom_almost_equals(pt.geometry, decimal=3)) & (self.allpoints.index != pt.name)]
                if not duplicatepts.empty:
                    if all(duplicatepts.pointtype != 'COLUMN') and all(
                            duplicatepts.set_geometry('polygon').polygon.area <= pt.polygon.area):
                        for col in ['p1', 'p2']:
                            self.alllines.loc[self.alllines[col].isin(duplicatepts.index), col] = pt.name
                        for col in ['p1', 'p2', 'p3', 'p4']:
                            self.allareas.loc[self.allareas[col].isin(duplicatepts.index), col] = pt.name

                        self.allpoints = self.allpoints.drop(duplicatepts.index)

        self._updategeometry()

    def _splitlinesbypoints(self):
        if self.lines.empty:
            return

        newlines = []
        for i, row in self.lines.iterrows():
            line = row['geometry']
            closepts = self._getclosegeometry(self.points, line)
            closepts = closepts[closepts.intersects(line)]
            if not closepts.empty:
                newlines.append(split(line, closepts.geometry.unary_union))
            else:
                newlines.append(line)

        self.lines.geometry = newlines
        self.lines = self.lines.reset_index(drop=False)
        self.lines = self.lines.explode()
        self.lines = self.lines.reset_index(drop=True)

        # Create new name
        alllinesidx = set(self.alllines.index)
        for i, ids in self.lines.groupby('name')['name']:
            if len(ids) <= 1:
                continue

            idxoverlap = 0
            while True:
                newidx = set(ids + '_' + (np.arange(len(ids)) + idxoverlap + 1).astype(str))
                overlap = len(newidx.intersection(alllinesidx))

                if overlap == 0:
                    break
                else:
                    idxoverlap += overlap

            self.lines.loc[self.lines.name == i, 'name'] = list(newidx)

        # If the name if used
        self.lines = self.lines.set_index('name')

    def _splitareasbypoints(self):
        if self.areas.empty:
            return

        newareas = []
        for i, row in self.areas.iterrows():
            area = row['geometry']
            closepts = self._getclosegeometry(self.points, area)
            closepts = closepts[closepts.intersects(area)]
            if not closepts.empty:
                newareas.append(split(area, closepts.geometry.unary_union))
            else:
                newareas.append(area)

        self.areas.geometry = newareas
        self.areas = self.areas.reset_index(drop=False)
        self.areas = self.areas.explode()
        self.areas = self.areas.reset_index(drop=True)

        # Create new name
        allareasidx = set(self.allareas.index)
        for i, ids in self.areas.groupby('name')['name']:
            if len(ids) <= 1:
                continue

            idxoverlap = 0
            while True:
                newidx = set(ids + '_' + (np.arange(len(ids)) + idxoverlap + 1).astype(str))
                idxoverlap += len(newidx.intersection(allareasidx))
                overlap = len(newidx.intersection(allareasidx))

                if overlap == 0:
                    break
                else:
                    idxoverlap += overlap

            self.areas.loc[self.areas.name == i, 'name'] = list(newidx)

        self.areas = self.areas.set_index('name')

    def _snaplinestopoints(self):
        if self.lines.empty:
            return

        ptnames = []
        ptnames.extend(list(self.lines.p1))
        ptnames.extend(list(self.lines.p2))
        pointpolys = self.points.set_geometry('polygon')

        newlines = []
        for i, row in self.lines.iterrows():
            line = row['geometry']
            line_coords = line.coords[:]
            end_nodes_id = [None, None]

            closepts = self._getclosegeometry(pointpolys, line)
            if not closepts.empty:
                for end in [0, -1]:
                    endpoint = Point(line_coords[end])
                    dist = closepts.geometry.centroid.distance(endpoint)
                    j = dist.idxmin()
                    line_coords[end] = self.points.loc[j, 'geometry'].coords[0]
                    end_nodes_id[end] = j

            self.lines.loc[i, ['p1', 'p2']] = end_nodes_id
            newlines.append(LineString(line_coords))

        self.lines.geometry = newlines
        self.lines = self.lines[((self.lines.linetype == 'COLUMN') | (self.lines.p1 != self.lines.p2))]

    def _snapareastopoints(self):
        if self.areas.empty:
            return

        ptnames = []
        ptnames.extend(list(self.areas.p1))
        ptnames.extend(list(self.areas.p2))
        pointpolys = self.points.set_geometry('polygon')

        newareas = []
        for i, row in self.areas.iterrows():
            area = row['geometry']
            area_coords = area.coords[:]
            end_nodes_id = [None, None]

            closepts = self._getclosegeometry(pointpolys, area)
            if not closepts.empty:
                for end in [0, -1]:
                    endpoint = Point(area_coords[end])
                    dist = closepts.geometry.centroid.distance(endpoint)
                    j = dist.idxmin()
                    area_coords[end] = self.points.loc[j, 'geometry'].coords[0]
                    end_nodes_id[end] = j

            self.areas.loc[i, ['p1', 'p2', 'p3', 'p4']] = end_nodes_id + end_nodes_id[::-1]
            newareas.append(LineString(area_coords))

        self.areas.geometry = newareas
        self.areas = self.areas[((self.areas.areatype == 'COLUMN') | (self.areas.p1 != self.areas.p2))]

    def _snapisolatedendpoints(self):
        for i, pt in self.points.iterrows():
            connectedptnames = []
            connectedptnames.extend(self._connectedpointstolines(pt))
            connectedptnames.extend(self._connectedpointstoareas(pt))
            if len(connectedptnames) == 1:
                closepts = self._getclosegeometry(self.points.set_geometry('polygon'), pt['geometry'])
                closepts = closepts[closepts.intersects(pt['geometry'])]
                largestpt = closepts.loc[closepts.geometry.area.idxmax()]

                self.points.loc[i, 'geometry'] = largestpt['geometry']

    def _snaptolargestpoints(self):
        ptsnocolumns = self.notcolumns().set_geometry('polygon')
        for i, pt in ptsnocolumns.iterrows():
            closepts = self._getclosegeometry(ptsnocolumns, pt['geometry'])
            closepts = closepts[closepts.intersects(pt['geometry'])]
            if not closepts.empty:
                largestpt = closepts.loc[closepts.polygon.area.idxmax()]
                if largestpt.polygon.area > pt.polygon.area:
                    self.points.loc[i, 'geometry'] = largestpt['geometry']

    def _snaptocolumns(self):
        columns = self.not_incore(self.columns())

        for i, pt in columns.iterrows():
            closepts = self._getclosegeometry(self.points, pt.polygon)
            closepts = closepts[closepts.within(pt.polygon)]

            for j, closept in closepts.iterrows():
                self.points.loc[j, 'geometry'] = pt.geometry

    @staticmethod
    def _getextrapolatedline(p1, p2):
        """Creates a line extrapoled in p1->p2 direction"""
        extrapolate_ratio = 10
        a = p2
        b = (p2.x + extrapolate_ratio * (p2.x - p1.x), p2.y + extrapolate_ratio * (p2.y - p1.y))
        return LineString([a, b])

    def _extendline(self, ptincolumn, ptnotincolumn, polygon):
        polygon_ext = LinearRing(polygon.exterior.coords)  # we only care about the boundary intersection
        long_line = self._getextrapolatedline(ptnotincolumn, ptincolumn)

        if polygon_ext.intersects(long_line):
            intersection_point = polygon_ext.intersection(long_line)
            if intersection_point.geom_type == 'MultiPoint':
                intersection_point = list(intersection_point)[0]
            new_point_coords = list(intersection_point.coords)[0]  #
            return Point(new_point_coords)
        else:
            old_point_coords = ptincolumn.coords
            return Point(old_point_coords)

    def _extendisolatedlinesincolumn(self):
        # For each column...
        for i, pt in self.columns().iterrows():
            # Find the points inside the column
            closepts = self._getclosegeometry(self.points, pt.polygon)
            closepts = closepts[closepts.within(pt.polygon) & (closepts.index != pt.name)]

            # Get the lines and areas attached to them
            closelines = pd.concat([self._lineswithpoints(closepts.index), self._areaswithpoints(closepts.index)],
                                   sort=False).set_geometry('geometry')

            # For each line in the column, extend it to the edge of the column if it is isolated
            for j, line in closelines.iterrows():
                if line.p1 in closepts.index:
                    ptincolumn = line.p1
                    ptnotincolumn = line.p2
                else:
                    ptincolumn = line.p2
                    ptnotincolumn = line.p1

                connectedptnames = []
                connectedptnames.extend(self._connectedpointstolines(self.points.loc[ptincolumn, :]))
                connectedptnames.extend(self._connectedpointstoareas(self.points.loc[ptincolumn, :]))
                if len(connectedptnames) == 1:
                    newpt = self._extendline(self.points.loc[ptincolumn, 'geometry'],
                                             self.points.loc[ptnotincolumn, 'geometry'], pt.polygon)
                    self.points.loc[ptincolumn, 'geometry'] = newpt

            # Update the geometry
            self._updategeometry()
            closepts = self.points.loc[closepts.index]
            closelines = pd.concat([self._lineswithpoints(closepts.index), self._areaswithpoints(closepts.index)],
                                   sort=False).set_geometry('geometry')

            # Using the updated geometry, find the intersecting points of the extended lines and bring them back
            for j, closept in closepts.iterrows():
                closeline = closelines[(closelines.p1 == closept.name) | (closelines.p2 == closept.name)]
                if not closeline.empty:
                    line = closeline.geometry.values[0]
                    intersectingpts = unary_union(line.intersection(closelines.geometry.unary_union.difference(line)))
                    if not intersectingpts.is_empty:
                        self.points.loc[j, 'geometry'] = nearest_points(closept.geometry, intersectingpts)[1]

                        # if intersectingpts.geom_type == 'MultiPoint':
                        #     distances = [closept.geometry.distance(intpt) for intpt in intersectingpts]
                        #     furthestpt = intersectingpts[distances.index(max(distances))]
                        # elif intersectingpts.geom_type == 'Point':
                        #     self.points.loc[j, 'geometry'] = intersectingpts

            self._updategeometry()

    def _movepointstocolumnedge(self):
        columns = self.incore(self.columns())

        # For each column in the core...
        for i, pt in columns.iterrows():
            # Find the points inside the column
            closepts = self._getclosegeometry(self.points, pt.polygon)
            closepts = closepts[closepts.within(pt.polygon)]

            # Find the lines inside the column
            closelines = pd.concat([self._lineswithpoints(closepts.index), self._areaswithpoints(closepts.index)],
                                    sort=False).set_geometry('geometry')
            closelines.geometry = closelines.geometry.apply(lambda geom: geom.difference(pt.polygon))

            # Duplicate common points in the column
            ptnames = closelines[['p1', 'p2']].values.flatten()
            unique_pts, count_pts = np.unique(ptnames, return_counts=True)
            usedpts = dict(zip(unique_pts, count_pts))

            # loop through each used point and duplicate it if required
            for usedpt, count in usedpts.items():
                if (count > 1) or (usedpt == pt.name):

                    # Find duplicate points
                    duppt = self.points[self.points.index == usedpt]

                    # Create the duplicates and rename
                    newpts = duppt.iloc[np.arange(len(duppt)).repeat(count)].copy()
                    newpts.index = ['"{}_{}"'.format(usedpt.replace('"', ''), i + 1) for i in range(count)]

                    # Make sure column isnt duplicated
                    newpts.loc[newpts.pointtype == 'COLUMN', 'pointtype'] = 'BEAM'

                    # Append to the points list
                    ptnames[ptnames == usedpt] = newpts.index
                    if usedpt != pt.name:
                        self.points = self.points[self.points.index != usedpt]
                    self.points = self.points.append(newpts, sort=False, verify_integrity=True)

            # Reassign p1 and p2
            closelines[['p1', 'p2']] = np.reshape(ptnames, [len(closelines), 2])

            # # Remove lines which are completely inside the column
            # closelines = closelines[~closelines.geometry.is_empty]

            for j, line in closelines.iterrows():
                if line.geometry.geom_type == 'LineString':
                    # Move points to end of lines
                    coords = line.geometry.coords[:]
                    if len(coords) == 0:
                        coords = pt.geometry.coords[:]

                    self.points.loc[line.p1, 'geometry'] = Point(coords[0])
                    self.points.loc[line.p2, 'geometry'] = Point(coords[-1])
                    if not pd.isna(line.linetype):
                        self.lines.loc[j, ['p1', 'p2']] = [line.p1, line.p2]
                        self.lines.loc[j, 'geometry'] = line.geometry
                    elif not pd.isna(line.areatype):
                        self.areas.loc[j, ['p1', 'p2', 'p3', 'p4']] = [line.p1, line.p2] * 2
                        self.areas.loc[j, 'geometry'] = line.geometry

        self._updategeometry()

    def _createrigidlinkfrompoints(self, p1, p2):

        links = {
            'name': [],
            'property': [],
            'p1': [],
            'p2': [],
        }

        for pts in zip(p1, p2):
            links = {
                'name': links['name'] + ['R{}_{}_{}'.format(self.story, pts[0].replace('"', ''), pts[1].replace('"', ''))],
                'property': links['property'] + ['RIGID'],
                'p1': links['p1'] + [pts[0]],
                'p2': links['p2'] + [pts[1]],
            }

        rigidlinks = pd.DataFrame(links).set_index('name')
        rigidlinks.index.name = 'name'
        self.links = self.links.append(rigidlinks)
        self._updategeometry()

    def _connectcolumnstolines(self):
        columns = self.incore(self.columns())

        for i, col in columns.iterrows():
            # Find the points inside the column
            closepts = self._getclosegeometry(self.points, col.polygon)
            closepts = closepts[closepts.within(col.polygon) & (closepts.pointtype != 'COLUMN')]

            self._createrigidlinkfrompoints([col.name] * len(closepts), closepts.index)


    ####################################################################################################################
    # Write
    ####################################################################################################################

    def _updatealllines(self):
        if self.lines.empty:
            return

        # Get the new lines
        self.lines['level'] = self.story
        self.lines.index.name = 'name'

        # Append new lines
        newlines = self.lines.loc[~self.lines.index.isin(self.alllines.index)]
        newlines.index.name = 'name'
        self.alllines = self.alllines.append(newlines[['linetype', 'p1', 'p2', 'geometry']])

        # Update existing lines
        self.alllines.loc[self.lines.index, ['linetype', 'p1', 'p2', 'geometry']] = \
            self.lines[['linetype', 'p1', 'p2', 'geometry']]

        # Delete unused line assignments
        usedlines = self.lineassigns.loc[(self.story, self.lines.index), :]
        self.lineassigns = self.lineassigns.loc[self.lineassigns.index.get_level_values(0) != self.story, :]
        self.lineassigns = self.lineassigns.append(usedlines)

        # Append new line assignments
        newlineassigns = self.lines.loc[~self.lines.index.isin(self.lineassigns.loc[self.story, :].index)]
        self.lineassigns = self.lineassigns.append(newlineassigns.reset_index().set_index(['level', 'name'])[['section', 'angle']])

        # Update lines assignments
        self.lineassigns = self.lineassigns.sort_index()
        self.lineassigns.loc[(self.story, self.lines.index), ['section', 'angle']] = \
            self.lines.reset_index().set_index(['level', 'name'])[['section', 'angle']]

    def _updatealllinks(self):
        if self.links.empty:
            return

        # Get the new lines
        self.links['level'] = self.story
        self.links.index.name = 'name'

        # Append new lines
        newlinks = self.links.loc[~self.links.index.isin(self.alllinks.loc[self.alllinks.level == self.story, :].index)]
        newlinks.index.name = 'name'
        self.alllinks = self.alllinks.append(newlinks[['level', 'p1', 'p2', 'geometry']])

        # Update existing lines
        self.alllinks.loc[self.links.index, ['level', 'p1', 'p2', 'geometry']] = \
            self.links[['level', 'p1', 'p2', 'geometry']]

        # Append new line assignments
        newlinkassigns = self.links.loc[~self.links.index.isin(self.linkassigns.index)]
        self.linkassigns = self.linkassigns.append(newlinkassigns[['property']])

        # Update lines assignments
        self.linkassigns.loc[self.linkassigns.index.isin(self.links.index), 'property'] = \
            self.links['property']

    def _updateallareas(self):
        if self.areas.empty:
            return

        # Set the level
        self.areas['level'] = self.story
        self.areas.index.name = 'name'

        # Append new areas
        newareas = self.areas[~self.areas.index.isin(self.allareas.index)] # make sure it doesnt exist
        newareas.index.name = 'name'
        self.allareas = self.allareas.append(newareas[['p1', 'p2', 'p3', 'p4', 'geometry', 'areatype']])

        # Update existing areas
        self.allareas.loc[self.areas.index, ['p1', 'p2', 'p3', 'p4', 'geometry', 'areatype']] = \
            self.areas[['p1', 'p2', 'p3', 'p4', 'geometry', 'areatype']]

        # Delete unused area assignments
        usedareas = self.areaassigns.loc[(self.story, self.areas.index), :]
        self.areaassigns = self.areaassigns.loc[self.areaassigns.index.get_level_values(0) != self.story, :]
        self.areaassigns = self.areaassigns.append(usedareas)

        # Append new area assignments
        newareaassigns = self.areas[~self.areas.index.isin(self.areaassigns.loc[self.story, :].index)] # make sure it doesnt exist
        self.areaassigns = self.areaassigns.append(newareaassigns.reset_index().set_index(['level', 'name'])[['section']])
        self.areaassigns.index.name = 'name'

        self.areaassigns = self.areaassigns.sort_index()
        self.areaassigns.loc[(self.story, self.areas.index), ['section']] = \
            self.areas.reset_index().set_index(['level', 'name'])[['section']]

    def _updateallpoints(self):
        if self.points.empty:
            return

        # Update x, y
        self.points.loc[:, 'x'] = self.points.geometry.x
        self.points.loc[:, 'y'] = self.points.geometry.y

        # Append new points
        self.allpoints = pd.concat([self.allpoints, self.points.loc[
            ~self.points.index.isin(self.allpoints.index), ['x', 'y', 'z', 'geometry']]], sort=False)
        self.allpoints.index.name = 'name'

        # Save movements
        self.allpoints.loc[self.points.index, 'dx'] = \
            self.allpoints.loc[self.points.index, 'x'].astype(int) - self.points.loc[:, 'x'].astype(int)
        self.allpoints.loc[self.points.index, 'dy'] = \
            self.allpoints.loc[self.points.index, 'y'].astype(int) - self.points.loc[:, 'y'].astype(int)

        # Update x, y, z, and geometry
        self.allpoints.loc[self.points.index, ['x', 'y', 'z', 'geometry']] = self.points[['x', 'y', 'z', 'geometry']]

        usedpoints = self._getpoints(self.alllines, self.allareas)
        self.allpoints = self.allpoints.loc[usedpoints.index]

    def _updateallgeometry(self):
        self._updategeometry()
        self._updatealllines()
        self._updatealllinks()
        self._updateallareas()
        self._updateallpoints()

    def _writeheading(self, heading, ln_list):
        if heading not in list(self._headings.keys()):
            self._filelines.append('$ {}\n'.format(heading))
            self._filelines.extend(ln_list)
            return

        next_heading = self._nextheading(heading)

        start_idx = self._headings[heading]
        end_idx = self._headings[next_heading] if next_heading is not None else len(self._filelines)

        self._filelines[(start_idx + 1):end_idx] = ln_list
        self._getheadings()

    def writepointmovements(self, file):
        self.allpoints.x = self.allpoints.apply(lambda row: row.geometry.x, axis=1)
        self.allpoints.y = self.allpoints.apply(lambda row: row.geometry.y, axis=1)

        self.allpoints.reset_index(drop=False).drop('geometry', axis=1).to_csv(file, index=False)

    def writee2k(self, file):
        self._writee2k_linkprops()

        self._writee2k_points()
        self._writee2k_lines()
        self._writee2k_links()
        self._writee2k_areas()

        self._writee2k_lineassigns()
        self._writee2k_linkassigns()
        self._writee2k_areaassigns()

        with open(file, 'w') as f:
            f.writelines(self._filelines)

    def _writee2k_points(self):
        self.allpoints.x = self.allpoints.apply(lambda row: row.geometry.x, axis=1)
        self.allpoints.y = self.allpoints.apply(lambda row: row.geometry.y, axis=1)

        ln_list = []
        for i, row in self.allpoints.reset_index(drop=False).drop('geometry', axis=1).iterrows():
            z = int(row['z'])
            if z == 0:
                z = ''
            pt = 'POINT "{0}" {1} {2} {3}\n'.format(row['name'], int(row['x']), int(row['y']), z)
            ln_list.append(pt)

        heading = 'POINT COORDINATES'
        self._writeheading(heading, ln_list)

    def _writee2k_lines(self):
        lnslist = []
        for i, row in self.alllines.reset_index(drop=False).drop('geometry', axis=1).iterrows():
            z = 0
            if row.p1 == row.p2:
                z = 1
            ln = 'LINE "{0}" {1} "{2}" "{3}" {4}\n'.format(row['name'], row['linetype'], row['p1'], row['p2'], z)
            lnslist.append(ln)

        heading = 'LINE CONNECTIVITIES'
        self._writeheading(heading, lnslist)

    def _writee2k_links(self):
        lnslist = []
        for i, row in self.alllinks.reset_index(drop=False).drop('geometry', axis=1).iterrows():
            ln = 'LINK "{0}" POINT1 "{1}" "{2}" POINT2 "{1}" "{3}"\n'.format(row['name'], row['level'], row['p1'], row['p2'])
            lnslist.append(ln)

        heading = 'LINK CONNECTIVITIES'
        self._writeheading(heading, lnslist)

    def _writee2k_areas(self):
        ln_list = []
        for i, row in self.allareas.reset_index(drop=False).drop('geometry', axis=1).iterrows():
            ln = 'AREA "{0}" {1} 4 "{2}" "{3}" "{4}" "{5}" 0 0 1 1 \n'.format(row['name'], row['areatype'], row['p1'], row['p2'], row['p3'], row['p4'])
            ln_list.append(ln)

        heading = 'AREA CONNECTIVITIES'
        self._writeheading(heading, ln_list)

    def _writee2k_linkprops(self):
        rigid = ['LINKPROP "RIGID" TYPE "LINEAR" \n',
                 'LINKPROP "RIGID" DOF "U1" FIXED "Yes" \n',
                 'LINKPROP "RIGID" DOF "U2" FIXED "Yes" \n',
                 'LINKPROP "RIGID" DOF "U3" FIXED "Yes" \n',
                 'LINKPROP "RIGID" DOF "R1" FIXED "Yes" \n',
                 'LINKPROP "RIGID" DOF "R2" FIXED "Yes" \n',
                 'LINKPROP "RIGID" DOF "R3" FIXED "Yes" \n']

        heading = 'LINK PROPERTIES'
        self._writeheading(heading, rigid)

    def _writee2k_lineassigns(self):
        ln_list = []
        for i, row in self.lineassigns.reset_index(drop=False).iterrows():
            ln = 'LINEASSIGN "{0}" "{1}" SECTION "{2}" ANG {3}\n'.format(row['name'], row['level'], row['section'], row['angle'])
            ln_list.append(ln)

        heading = 'LINE ASSIGNS'
        self._writeheading(heading, ln_list)

    def _writee2k_linkassigns(self):
        ln_list = []
        for i, row in self.linkassigns.reset_index(drop=False).iterrows():
            ln = 'LINKASSIGN "{0}" PROPERTY "{1}"\n'.format(row['name'], row['property'])
            ln_list.append(ln)

        heading = 'LINK ASSIGNS'
        self._writeheading(heading, ln_list)

    def _writee2k_areaassigns(self):
        ln_list = []
        for i, row in self.areaassigns.reset_index(drop=False).iterrows():
            ln = 'AREAASSIGN "{0}" "{1}" SECTION "{2}"\n'.format(row['name'], row['level'], row['section'])
            ln_list.append(ln)

        heading = 'AREA ASSIGNS'
        self._writeheading(heading, ln_list)

    ####################################################################################################################
    # Other
    ####################################################################################################################

    @staticmethod
    def _numtostring(n):
        string = ""
        while n > 0:
            n, remainder = divmod(n - 1, 26)
            string = chr(65 + remainder) + string
        return string

    def _convertcolumns(self):
        cols = self.lines[self.lines['linetype'] == 'COLUMN']
        self.lines.loc[cols.index, 'geometry'] = cols.apply(lambda row: self.points.loc[row.p1, 'geometry'],
                                                            axis=1).values

    def _updategeometry(self):
        if not self.points.empty:
            self.points.polygon = self.points.set_geometry('polygon').apply(
                lambda row: affinity.translate(row['polygon'], xoff=(row['geometry'].x - row['polygon'].centroid.x), yoff=(row['geometry'].y - row['polygon'].centroid.y)),
                axis=1)
        if not self.lines.empty:
            self.lines.geometry = self.lines.apply(
                lambda row: LineString([self.points.loc[row.p1, 'geometry'], self.points.loc[row.p2, 'geometry']]),
                axis=1)
        if not self.areas.empty:
            self.areas.geometry = self.areas.apply(
                lambda row: LineString([self.points.loc[row.p1, 'geometry'], self.points.loc[row.p2, 'geometry']]),
                axis=1)

    def _simplifylinestopoints(self):
        for i, row in self.lines.iterrows():
            coords = list(row.geometry.coords)
            if len(set(coords)) == 1:
                self.lines.loc[i, 'geometry'] = Point(coords[0])

    ####################################################################################################################
    # Sections
    ####################################################################################################################

    def _createcolumnsection(self, pt, cols):
        if pt.name not in self.points.index:
            return

        valididx = set(cols.section).intersection(set(self.sections.index))
        if not valididx:
            self.points.loc[pt.name, 'pointtype'] = cols.linetype.values[0]
            self.points.loc[pt.name, 'section'] = cols.section.values[0]
            self.points.loc[pt.name, 'polygon'] = pt.geometry.buffer(500)
            return

        col = cols[cols.section.isin(valididx)].iloc[0]
        self.points.loc[pt.name, 'pointtype'] = col.linetype
        self.points.loc[pt.name, 'section'] = col.section



        x = float(self.sections.loc[col.section, 'D'])
        y = float(self.sections.loc[col.section, 'B'])
        buffer = 5

        poly = Polygon([[pt.geometry.x - (x / 2 + buffer), pt.geometry.y - (y / 2 + buffer)],
                        [pt.geometry.x - (x / 2 + buffer), pt.geometry.y + (y / 2 + buffer)],
                        [pt.geometry.x + (x / 2 + buffer), pt.geometry.y + (y / 2 + buffer)],
                        [pt.geometry.x + (x / 2 + buffer), pt.geometry.y - (y / 2 + buffer)]])

        poly = affinity.rotate(poly, angle=float(col.angle), origin='centroid')
        self.points.loc[pt.name, 'polygon'] = poly

    def _createlinesection(self, pt, lines):
        lines = lines[lines.section != '"RIGID"']
        if lines.empty or pt.name not in self.points.index:
            return

        valididx = set(lines.section).intersection(set(self.sections.index))
        if not valididx:
            self.points.loc[pt.name, 'pointtype'] = lines.linetype.values[0]
            self.points.loc[pt.name, 'section'] = lines.section.values[0]
            self.points.loc[pt.name, 'polygon'] = pt.geometry.buffer(500)
            return

        sectionwidths = self.sections.loc[lines.section, 'B'].astype(float)
        largestsection = sectionwidths.idxmax()

        self.points.loc[pt.name, 'pointtype'] = lines.loc[lines.section == largestsection, 'linetype'].values[0]
        self.points.loc[pt.name, 'section'] = largestsection
        self.points.loc[pt.name, 'polygon'] = pt.geometry.buffer(sectionwidths.max()/2 + 2)

    def _createareasection(self, pt, areas):
        if pt.name not in self.points.index:
            return

        valididx = set(areas.section).intersection(set(self.sections.index))
        if not valididx:
            self.points.loc[pt.name, 'pointtype'] = areas.areatype.values[0]
            self.points.loc[pt.name, 'section'] = areas.section.values[0]
            self.points.loc[pt.name, 'polygon'] = pt.geometry.buffer(500)
            return

        sectionwidths = self.areaprop.loc[areas.section, 'TB'].astype(float)
        largestsection = sectionwidths.idxmax()

        self.points.loc[pt.name, 'pointtype'] = areas.loc[areas.section == largestsection, 'areatype'].values[0]
        self.points.loc[pt.name, 'section'] = largestsection
        self.points.loc[pt.name, 'polygon'] = pt.geometry.buffer(sectionwidths.max()/2 + 2)

    def _createpointsections(self):
        for i, pt in self.points.iterrows():
            lines = self._lineswithpoints([pt.name])
            if not lines.empty:
                if any(lines.linetype == 'COLUMN'):
                    self._createcolumnsection(pt, lines[lines.linetype == 'COLUMN'])
                else:
                    self._createlinesection(pt, lines[lines.linetype != 'COLUMN'])
            else:
                areas = self._areaswithpoints([pt.name])
                if not areas.empty:
                    self._createareasection(pt, areas)

    def plot_story(self, story, ax=None):
        if self.story != story:
            self._getstory(story)

        if ax is None:
            fig, ax = plt.subplots()
            fig.suptitle(story)
            ax.set_xlabel('x')
            ax.set_ylabel('y')

        if not self.grid.empty:
            self.grid.plot(ax=ax, color='k', linestyle='--', linewidth=1)
            self.grid.apply(
                lambda row: ax.annotate(row.label, xy=(row.xa, row.ya), xytext=(-7.5, 2.5), textcoords='offset points'),
                axis=1)

        if not self.lines.empty:
            self.lines.plot(ax=ax, color='b')

        if not self.areas.empty:
            self.areas.plot(ax=ax, color='b', linestyle='--', linewidth=3)

        if not self.links.empty:
            self.links.plot(ax=ax, color='r')

        if self.points.empty:
            return

        if not self.notcolumns().empty:
            self.notcolumns().set_geometry('polygon').plot(ax=ax, color='m', markersize=10)

        if not self.columns().empty:
            self.columns().set_geometry('polygon').plot(ax=ax, color='c', markersize=10)

        if not self.points[self.points.lockedx & self.points.lockedy].empty:
            self.points[self.points.lockedx & self.points.lockedy].plot(ax=ax, color='g', markersize=10)

        if not self.points[(~self.points.lockedx & self.points.lockedy)].empty:
            self.points[(~self.points.lockedx & self.points.lockedy)].plot(ax=ax, color='y', marker='>', markersize=10)

        if not self.points[(self.points.lockedx & ~self.points.lockedy)].empty:
            self.points[(self.points.lockedx & ~self.points.lockedy)].plot(ax=ax, color='y', marker='^', markersize=10)

        if not self.points[~self.points.lockedx & ~self.points.lockedy].empty:
            self.points[~self.points.lockedx & ~self.points.lockedy].plot(ax=ax, color='r', markersize=10)

    def plot_networks(self):
        fig, ax = plt.subplots()

        if not self.lines.empty:
            self.lines.plot(ax=ax)
            for i, row in self.subnetworks.iterrows():
                self.points.loc[row.nodes, :].plot(ax=ax)
