import imagej

global GLVector, jFloat, jArray


class ScyView(dict):
    ij = None

    # Config could be read from file
    def config(self):
        self['fiji_directory'] = './Fiji.app'
        return self

    def run(self, cmd='sc.iview.commands.LaunchViewer', args={}):
        if (args == {}):
            return self.ij.command().run(cmd, True).get()
        else:
            # print(list(args.keys())[0] + '\t' +
            # str(args[list(args.keys())[0]]))
            return self.ij.command().run(
                cmd,
                True,
                list(args.keys())[0],
                str(args[list(args.keys())[0]])).get()

    def create(self):
        self.ij = imagej.init(self['fiji_directory'], headless=False)
        import jnius
        global GLVector, jArray, jFloat
        jArray = jnius.autoclass("java.lang.reflect.Array")
        jFloat = jnius.autoclass("java.lang.Float")
        GLVector = jnius.autoclass('cleargl.GLVector')
        self.ij.ui().showUI()
        return self.run().getOutput('sciView')

    def glvector(self, x, y, z):
        global jArray, jFloat
        a = jArray.newInstance(jFloat, 3)
        a[0] = jFloat(x)
        a[1] = jFloat(y)
        a[2] = jFloat(z)
        return a
