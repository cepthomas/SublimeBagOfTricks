using System;
using System.Collections.Generic;
using System.IO;
using System.Text;

namespace NBagOfTricks.Utils
{
    /// <summary>
    /// Dumps: objects, dictionaries of objects, or lists of objects.
    /// Output format is modified json.
    /// </summary>
    public class Dumper    {
        /// <summary>Output writer.</summary>
        TextWriter _writer = null;

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
public Dumper(TextWriter writer){_writer = writer;}
#endregion

        #endregion

        /// <summary>
        /// Top level writer.
        /// </summary>
        /// <param name="obj"></param>
        public void Write(object obj)
        {
            int xxxx = 999;

            switch(obj)            {
                case Dictionary<string, object> dict:                      Write(dict);                    break;

                case List<object> list:                    Write(list);                    break;

default: // simple
string s = $"{obj}";
WriteIndented(s);
break;
}
}
    }
}
