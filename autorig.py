""" BUGGY!!!
You can reproduce a closed graph of nodes by selecting them, and storing the printout of the object in print_everything()
To recreate your graph, just pass the arguments to the object.

It does not work if the nodes outside of the graph are not in the scene with the same name. It will work for 'time1' because it is in every scene for exemple, but not for any other nodes.
"""
import logging
import itertools
import maya.cmds as cmds
logger = logging.getLogger(__name__)


def pairwise(iterable):
    """Iterate two by two from an iterable."""
    a = iter(iterable)
    return itertools.izip(a, a)


class AutoRigger(object):
    def __init__(self, oldNodes={}, newAttributes={}, connections=[], attributes = {}, expressions={}):
        self.newNodes = {}
        self.oldNodes = oldNodes
        self.attributes = attributes
        self.expressions = expressions
        self.newAttributes = newAttributes
        self.connections = connections
        if oldNodes:
            self.recreate()
        else:
            nodes = cmds.ls(sl=True)
            if nodes:
                self.get_nodes_by_type(nodes)
                self.getattributes()
                dest = cmds.listConnections(nodes, c=True, plugs=True, destination=True, source=False)
                source = cmds.listConnections(nodes, c=True, plugs=True, destination=False, source=True)
                self.constructcommand(dest, revert=False)
                self.constructcommand(source, revert=True)
                self.replace_nodes_string()
            self.print_everything()

    def get_nodes_by_type(self, nodes):
        """Classify every nodes in a dict by node type.
        Add the future string by which they will be called in the command.
        """
        for i in nodes:
            try:
                node, nodeType = cmds.ls(i, showType=True)
                self.oldNodes[nodeType].update({node: 'self.newNodes["{}"][{}]'.format(nodeType, len(self.oldNodes[nodeType]))})
            except KeyError:
                self.oldNodes[cmds.ls(i, showType=True)[1]] = {}
                self.oldNodes[nodeType].update({node: 'self.newNodes["{}"][{}]'.format(nodeType, len(self.oldNodes[nodeType]))})
        return self.oldNodes

    def getattributes(self):
        for key, nodes in self.oldNodes.iteritems():
            if key == 'expression':
                expression = True
            else:
                expression = False
            for oldNode in nodes:
                listAttr = cmds.listAttr(oldNode)
                if listAttr:
                    self.attributes[nodes[oldNode]] = {}
                    for attr in listAttr:
                        try:
                            self.attributes[nodes[oldNode]].update({attr: {'value': cmds.getAttr(oldNode + '.' + attr)}})
                            self.attributes[nodes[oldNode]][attr].update({'type': cmds.getAttr(oldNode + '.' + attr, type=True)})
                            if expression and attr == 'expression':
                                self.expressions.update({nodes[oldNode]: self.attributes[nodes[oldNode]][attr]['value']})
                        except RuntimeError as e:
                            pass
                        except ValueError as e:
                            pass

                listAttrCustom = cmds.listAttr(oldNode, userDefined=True)
                if listAttrCustom:
                    self.newAttributes[nodes[oldNode]] = {}
                    for attr in listAttrCustom:
                        try:
                            self.newAttributes[nodes[oldNode]].update({attr: {'type': cmds.getAttr(oldNode + '.' + attr, type=True)}})
                            if cmds.attributeQuery(attr, node=oldNode, minExists=True):
                                self.newAttributes[nodes[oldNode]][attr].update({'min': cmds.attributeQuery(attr, node=oldNode, min=True)})
                            if cmds.attributeQuery(attr, node=oldNode, maxExists=True):
                                self.newAttributes[nodes[oldNode]][attr].update({'max': cmds.attributeQuery(attr, node=oldNode, max=True)})
                        except RuntimeError as e:
                            pass
                        except ValueError as e:
                            pass

    def constructcommand(self, connections, revert=False):
        """Create a string command that will create the current connection state in a new setup."""
        if connections:
            for x, y in pairwise(connections):
                if revert:
                    x, y = y, x
                xsplit = x.split('.')[0]
                ysplit = y.split('.')[0]
                if xsplit != ysplit:
                    self.connections.append(['"{}"'.format(x), '"{}"'.format(y)])
        return self.connections

    def replace_nodes_string(self):
        """Replace the names of the node by their Python counterpart."""
        for nodeType, nodes in self.oldNodes.iteritems():
            for node, value in nodes.iteritems():
                self.connections = [[i.replace('"' + node, value + ' + "') for i in u] for u in self.connections]


    def print_everything(self):
        print 'oldNodes =', self.oldNodes
        print 'newAttributes =', self.newAttributes
        print 'connections =', self.connections
        print 'attributes =', self.attributes
        print 'expressions =', self.expressions


    def recreate(self):
        self.createnodes()
        self.createAttributes()
        self.connectattributes()
        self.setexpressions()
        self.setAttributes()


    def createnodes(self):
        for key, values in self.oldNodes.iteritems():
            count = len(values)
            self.newNodes[key] = []
            while count:
                self.newNodes[key].append(cmds.createNode(key))
                count -= 1

    def createAttributes(self):
        for node, attrs in self.newAttributes.iteritems():
            node = eval(node)
            cmds.select(node)
            for attr, values in attrs.iteritems():
                cmds.addAttr(longName=attr, attributeType=attrs[attr]['type'])
                try:
                    cmds.addAttr(node + '.' + attr, edit=True, minValue=attrs[attr]['min'][0])
                except KeyError:
                    pass
                try:
                    cmds.addAttr(node + '.' + attr, edit=True, maxValue=attrs[attr]['max'][0])
                except KeyError:
                    pass

    def connectattributes(self):
        """Connect everything."""
        for i in self.connections:
            try:
                if not cmds.isConnected(eval(i[0]), eval(i[1])):
                    cmds.connectAttr(eval(i[0]), eval(i[1]), force=True)
            except RuntimeError as e:
                logger.info(e)

    def setAttributes(self):
        for node, attrs in self.attributes.iteritems():
            node = eval(node)
            for attr, values in attrs.iteritems():
                try:
                    cmds.setAttr(node + '.' + attr, values['value'])
                except:
                    try:
                        cmds.setAttr(node + '.' + attr, values['value'], type=values['type'])
                    except Exception as e:
                        logger.info('\n' + node + '.' + attr + ' | ' + str(values))
                        logger.info(e)


    def setexpressions(self):
        for node, expression in self.expressions.iteritems():
            for nodes in self.oldNodes.itervalues():
                for oldNode, newNode in nodes.iteritems():
                    if expression.find(oldNode) != -1:
                        self.expressions[node] = self.expressions[node].replace(oldNode, eval(newNode))
        for node, expression in self.expressions.iteritems():
            cmds.setAttr(eval(node) + '.expression', expression, type='string')
