# -*- coding: utf-8 -*-
"""
    sphinx_ext.scad
    ~~~~~~~~~~~~~~~

    Include OpenSCAD models in Sphinx documents

    :copyright: 2021 by Roie R. Black
    :license: BSD, see LICENSE for details
"""
from sphinx.errors import SphinxError
from sphinx.util.nodes import set_source_info
from docutils.parsers.rst import Directive
from docutils import nodes, utils
from docutils.parsers.rst import directives

import os
import shutil
import hashlib
import posixpath

DEBUG = True

# the generated scad files will be placed here and processed
cwd = os.getcwd()
BUILD_TMPDIR = os.path.join(cwd,'_build','scad')
SCAD_DIR = os.path.join(os.path.dirname(cwd),'scad')

if(DEBUG):
    print("BUILD: ", BUILD_TMPDIR)
    print("SCAD:", SCAD_DIR)

class SCADExtError(SphinxError):
    category = 'SCAD extension error'

    def __init__(self, msg, stderr=None, stdout=None):
        if stderr:
            msg += '\n[stderr]\n' + stderr.decode(sys_encoding, 'replace')
        if stdout:
            msg += '\n[stdout]\n' + stdout.decode(sys_encoding, 'replace')
        SphinxError.__init__(self, msg)

class RenderSCADImage(object):
    """ process the file in BUILD_TMPDIR using openscad options"""

    def __init__(self, text, builder, scadopts):
        if(DEBUG):
            print("Rendering", text)
        self.text = text
        self.builder = builder
        self.scadopts = scadopts
        self.imagedir = os.path.join(os.getcwd(),'_build','scad')
        os.makedirs(BUILD_TMPDIR, exist_ok=True)


    def render(self):
        '''return name of final rendered image file'''

        # hash the scad text to generate the image file name
        # add scadopts to text
        hashtext = self.text + self.scadopts
        shasum = "%s.png" % hashlib.md5(hashtext.encode('utf-8')).hexdigest()

        # set the relative image path for img src references
        imagedir = os.path.join(self.builder.imgpath,'scad')

        # get the image src path
        relfn = posixpath.join(imagedir,shasum)

        # get the final location path for the image file
        outfn = os.path.join(self.builder.outdir, self.builder.imagedir, 'scad', shasum)

        if(DEBUG):
            print("rendering:", self.text)
            print("imagedir:",imagedir)
            print("outdir: ", self.builder.outdir)
            print("relfn:",relfn)
            print("outfn:",outfn)

        # see if we already have generated this image
        #if os.path.exists(outfn):
        #    return relfn, outfn

        tempdir = BUILD_TMPDIR
        curpath = os.getcwd()
        os.chdir(tempdir)

        # create scad file to process
        self.wrap_text()

        # run openscad to build png file output in in tempdir
        cmd = "openscad %s --quiet -o temp.png temp.scad" % self.scadopts
        if(DEBUG):
            print('CMD: ', cmd)

        status = os.system(cmd)
        assert 0 == status

        # restore working directory
        os.chdir(curpath)

        # copy final image to image dir
        imagepath = os.path.join(os.path.abspath(self.imagedir),'scad')
        if not os.path.exists(imagepath):
            os.makedirs(imagepath)
        if(DEBUG):
            print("Copying file from %s to %s" % (tempdir, outfn))
        shutil.copyfile(os.path.join(tempdir, "temp.png"), outfn)

        return relfn, outfn

    def wrap_text(self):
        # noting to do for openscad
        self.scad = self.text

        # write scad file
        if (DEBUG):
            print("Writing to temp.scad:", self.scad)

        f = open('temp.scad','w')
        f.write(self.scad)
        f.close()


class scad(nodes.General, nodes.Element):
    pass

class SCAD(Directive):

    has_content = True
    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = True
    option_spec = {
        'label': directives.unchanged,
        'name': directives.unchanged,
        'width': directives.unchanged,
        'align': directives.unchanged,
        'camera': directives.unchanged,
        'axes': directives.unchanged,
        'autocenter': directives.flag,
        'viewall': directives.flag,
    }

    def run(self):
        scadcode = '\n'.join(self.content)
        node = scad()
        node['scad'] = scadcode
        node['label'] = None
        node['docname'] = self.state.document.settings.env.docname

        # set alignment and image size style
        style = ''
        if 'width' in self.options:
            style += 'width=%s' % self.options['width']
        if 'align' in self.options:
            style += ' class="align-%s"' % self.options['align']
        node['style'] = style

        # generate openscad option set
        scadopts = ''
        if 'camera' in self.options:
            scadopts += '--camera=%s ' % self.options['camera']
        if 'axes' in self.options:
            scadopts  += '--view %s ' % self.options['axes']
        if 'viewall' in self.options:
            scadopts += "--viewall "
        if 'autocenter' in self.options:
            scadopts += "--autocenter"
        node['scadopts'] = scadopts

        ret = [node]
        set_source_info(self,node)
        return ret

def html_visit_scad(self, node):
    scad = node['scad']
    scadopts = node['scadopts']

    # render the scad code using specified options
    try:
        imagedir = self.builder.imgpath
        fname, relfn = RenderSCADImage(scad, self.builder, scadopts).render()
    except SCADExtError  as exc:
        msg = unicode(str(exc), 'utf-8', 'replace')
        sm = nodes.system_message(msg, type='WARNING', level=2,
                backrefs=[], source=node['scad'])
        raise nodes.SkipNode
        sm.walkabout(self)
        self.builder.warn('display scad %r: ' % node['scad'] + str(exc))
        raise nodes.SkipNode
    if fname is None:
        # something failed -- use text-only as a bad substitute
        self.body.append('<span class="scad">%s</span>' %
                         self.encode(node['scad']).strip())
    else:
         if (DEBUG):
             print("imagedir: ", imagedir)
             print("LINK TO", fname)
         c = ('<img src="%s" %s' % (fname,node['style']))
         self.body.append( c + '/>')
    raise nodes.SkipNode

def latex_visit_scad(self, node):
    self.body.append('$' + node['scad'] + '$')
    raise nodes.SkipNode

def latex_visit_displayscad(self, node):
    self.body.append(node['scad'])
    raise nodes.SkipNode

def setup(app):
    app.add_node(scad,
        latex=(latex_visit_scad, None),
        html=(html_visit_scad,None))
    app.add_directive('scad', SCAD)
