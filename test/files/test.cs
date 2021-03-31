using System; // keyword.control.import.cs, source.cs meta.path.cs
using System.Collections.Generic;
using System.IO;
using System.Text;

namespace NBagOfTricks.Utils // storage.type.namespace.cs, entity.name.namespace.cs
{
    /// <summary>
    /// Dumps: objects, dictionaries of objects, or lists of objects.
    /// Output format is modified json.
    /// </summary>
    public class Dumper // storage.modifier.access.cs, storage.type.class.cs, entity.name.class.cs
    {
        /// <summary>Output writer.</summary> // comment.block.documentation.cs entity.name.tag.begin.cs, comment.block.documentation.cs text.documentation.cs
        TextWriter _writer = null; // support.type.cs, variable.other.member.cs, keyword.operator.assignment.variable.cs, constant.language.cs

        /// <summary>Output indent.</summary>
        const int _indent = 0;

        #region Stuff
        /// <summary>Output indent size.</summary>
        int _indentSize = 4;

        string mystring = "eeeeeeeeee";

        string jjjjj = "rrrrrrrrr";

        #region Nested
        /// <summary>
        /// Constructor
        /// </summary>
        /// <param name="writer">Output stream</param>
        public Dumper(TextWriter writer)
        {
            _writer = writer;
        }
        #endregion

        #endregion

        /// <summary>
        /// Top level writer.
        /// </summary>
        /// <param name="obj"></param>
        public void Write(object obj)
        {
            int xxxx = 999;

            switch(obj)
            {
                case Dictionary<string, object> dict:
                    Write(dict);
                    break;

                case List<object> list:
                    Write(list);
                    break;

                default: // simple
                    string s = $"{obj}";
                    WriteIndented(s);
                    break;
            }
        }
    }
}
