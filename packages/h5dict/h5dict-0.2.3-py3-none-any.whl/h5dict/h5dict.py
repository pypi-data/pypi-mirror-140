import h5py
import sys

DEFAULT_FALLBACK = "representation"


def File(name, mode, conversions_filters=[], fallback_mode=DEFAULT_FALLBACK, **kwargs):
    """Opens a HDF5 file and intances a h5dict interface for it.

    Args:
        name (str): HDF5 file name.
        mode (str): Openning mode.
        conversions_filters (list): Filters to convert data.
        fallback_mode (string): Mode to deal with incompatible types:
            * `representatrion`: Stores representation with `format()`;
            * `pickle`: Stores pickled object.
        **kwargs (dicts): Keywork arguments to be passed to h5py.

    Returns:
        h5dict: h5dict interface object.
    """
    return h5dict.load(name, mode, conversions_filters, fallback_mode, **kwargs)


READ_MODES = ["r", "r+", "a"]
WRITE_MODES = ["r+", "w", "w-", "x", "a"]
TYPE_MK = "__type__"
KEY_TYPE_MK = "__keytype__"


class h5dict:
    def __init__(self, hdf5, name, mode, conv, fallback, parent=None, key=""):
        from .conversions import conversions
        from .conversions import pickle_to, pickle_from

        self.conversions = conv + conversions
        self.fallback = fallback
        if fallback == "representation":
            self.print_incompatible = True
            self.fb_to_convert = format
            self.fb_from_convert = lambda x: x
            self.fb_type = "representation"
        elif fallback == "pickle":
            self.print_incompatible = False
            self.fb_to_convert = pickle_to
            self.fb_from_convert = pickle_from
            self.fb_type = "pickle"
        self.conversions += [(self.fb_type, self.fb_to_convert, self.fb_from_convert)]
        self.hdf5 = hdf5
        self.name = name
        self.mode = mode.lower()
        self.groups = {}
        self.parent = parent
        self.key = key
        self.closed = False

    @classmethod
    def load(self, name, mode, conversions=[], fallback=DEFAULT_FALLBACK, **kwargs):
        return self(h5py.File(name, mode, **kwargs), name, mode, conversions, fallback)

    # CONTAINER TYPE METHODS
    def __setitem__(self, key, value):
        """Tryes to create a dataset with informed value, if unable creates groups and
            datasets indide thoes groups.

        Args:
            key (str): Dataser/group name.
            value: Data to be stored.

        Raises:
            RuntimeError: File not in write mode.
            ValueError: I/O operation on closed file.
        """
        self.check_closed()
        try:
            if len(key) == 2:
                filters = key[1]
                key = key[0]
            else:
                filters = {}
        except:
            filters = {}
        if self.in_write_mode():
            # If key is not string convert it and stores original type for back conversion on load
            key, key_t = self.convert_key(key)
            # Try to convert value to a compatible type
            if type(value) == str:
                t = "str"
            else:
                value, t = try_convert_from(value, self.conversions)
            # if value is a dict creates a group and store data on dict in it.
            if type(value) is dict:
                if key in self.hdf5:
                    del self.hdf5[key]
                group = self.instance(self.hdf5.create_group(key), key)
                for dkey in value:
                    group[dkey, filters] = value[dkey]
                self.groups[key] = group
            # Else stores data
            else:
                try:
                    self.write_ds(key, data=value, **filters)
                except TypeError:
                    self.write_ds(key, data=self.fb_to_convert(value), **filters)
                    t = self.fb_type
                    if self.print_incompatible:
                        path = self.get_path() + "/" + key
                        print(
                            "Warning: Tried to store incompatible type on {} in {}, storing {}.".format(
                                path, self.name, self.fb_type
                            ),
                            file=sys.stderr,
                        )
            # Stores key and data type
            if key_t != str:
                self.write_attr(key, attr=KEY_TYPE_MK, value=key_t.__name__)
            if t != None:
                self.write_attr(key, attr=TYPE_MK, value=t)
        else:
            raise RuntimeError("File is not in write mode.")

    def __getitem__(self, key):
        """Reads a dataset or a group from file.

        Args:
            key (str): Dataset/group name.

        Raises:
            RuntimeError: File not in read mode.
            ValueError: I/O operation on closed file.

        Returns:
            h5dict or data: Returns data on dataset or h5dict for group
        """
        self.check_closed()
        key, _ = self.convert_key(key)
        if key in self.groups:
            return self.groups[key]
        else:
            try:
                if TYPE_MK in self.hdf5[key].attrs.keys():
                    t = self.hdf5[key].attrs[TYPE_MK]
                    if type(t) is str:
                        if t == "str":
                            return self.hdf5[key].asstr()[()]
                        else:
                            data = self.hdf5[key][()]
                            return try_convert_to(data, t, self.conversions)
                    else:
                        return self.hdf5[key][()]
                else:
                    return self.hdf5[key][()]
            except TypeError:
                group = self.instance(self.hdf5[key], key)
                self.groups[key] = group
                return group

    def __contains__(self, key):
        """Checks if a dataset or group exists.

        Args:
            key (str): Dataset/group name.

        Returns:
            bool: Returns if key exists or not.
        """
        self.check_closed()
        return item in self.keys()

    def __delitem__(self, key):
        """Deletes a dataset or group from file.

        Args:
            key (str): Dataset/group name.
        """
        self.check_closed()
        key, _ = self.convert_key(key)
        # Remove dataset
        del self.hdf5[key]
        # try to remove from groups
        if key in self.groups:
            del self.groups[key]

    def __repr__(self):
        """Returns a string representation of this object.

        Returns:
            str: String representation.
        """
        return "<h5dict interface for " + self.hdf5.__repr__()[1:]

    def __len__(self):
        """Returns the number of groups and datasets on this file/group.

        Returns:
            int: Number of datasets and groups.
        """
        self.check_closed()
        return len(self.__keys())

    def __iter__(self):
        """Returns a iterable object of all datasets and groups.

        Returns:
            object: Iterable object.
        """
        self.check_closed()
        return self.keys().__iter__()

    def __enter__(self):
        """Method to enter a with block.

        Returns:
            h5dict: This h5dict interface.
        """
        self.check_closed()
        return self

    def __exit__(self, *_):
        """Method to exit a with block.

        !!! Attention
            Does not handle errors yet.
        """
        self.close()

    # INTERNAL USE METHODS
    def check_closed(self):
        if self.closed:
            raise ValueError("I/O operation on closed file.")

    def in_mode(self, modes):
        # Check if in mode
        self.check_closed()
        is_read = False
        for m in modes:
            if m in self.mode:
                is_read = True
        return is_read

    def instance(self, hdf5, key):
        # Instances a new h5dict object to wrap an h5py object
        self.check_closed()
        return h5dict(
            hdf5,
            self.name,
            self.mode,
            self.conversions,
            self.fallback,
            parent=self,
            key=key,
        )

    def convert_key(self, key):
        # converts keys to str
        if key != str:
            if "numpy.int" in str(type(key)):
                key = int(key)
            if "numpy.float" in str(type(key)):
                key = float(key)
            try:
                eval(type(key).__name__)
            except:
                raise TypeError(
                    "Type {} of key {} can not be used.".format(type(key).__name__, key)
                )
        return str(key), type(key)

    def write_ds(self, key, **args):
        # Writes a dataset, if dataset already exists replace it
        if key in self.hdf5:
            del self.hdf5[key]
        self.hdf5.create_dataset(key, **args)

    def write_attr(self, key, attr, value):
        # Store attributes
        self.hdf5[key].attrs[attr] = value

    def __keys(self):
        # Raw keys output
        self.check_closed()
        return self.hdf5.keys()

    def get_path(self):
        parent = self.parent
        path = "/" + self.key
        while parent != None:
            path = parent.key + "/" + path
            parent = parent.parent
        return path

    # EXTERNAL/INTERNAL USE METHODS
    def in_read_mode(self):
        """Check open mode is readble.

        Returns:
            bool: Result of the check.
        """
        return self.in_mode(READ_MODES)

    def in_write_mode(self):
        """Check open mode is writable.

        Returns:
            bool: Result of the check.
        """
        return self.in_mode(WRITE_MODES)

    def to_dict(self):
        """Converts all the data the current HDF5 file or group in dicts and lists.

        Returns:
            dict: Loaded data.
        """
        self.check_closed()
        d = dict()
        for key in self.hdf5.keys():
            g_or_d = self[key]
            if KEY_TYPE_MK in self.hdf5[key].attrs.keys():
                key_t = eval(self.hdf5[key].attrs[KEY_TYPE_MK])
                ckey = key_t(key)
            else:
                ckey = key
            if type(g_or_d) == type(self):
                d[ckey] = g_or_d.to_dict()
            else:
                d[ckey] = g_or_d
        if self.parent != None:
            if TYPE_MK in self.hdf5.attrs.keys():
                d = try_convert_to(d, self.hdf5.attrs[TYPE_MK], self.conversions)
        return d

    def keys(self):
        """List all keys in group.

        Returns:
            KeysViewHDF5: All keys in group.
        """
        return list(self.__keys())

    def tree_view(self, max_depth=-1, print_types=False, **control_args):
        """Prints a tree view of the hdf5 file.

        Args:
            max_depth (int, optional): Set a maximum depth to print. Defaults to -1.
            print_types (bool, optional): Print type of data contained in datasets.
        """
        self.check_closed()
        for arg in control_args:
            if not arg in ["name", "ident", "child_ident", "depth"]:
                raise TypeError(
                    "tree_view() got an unexpected keyword argument '{}'".format(arg)
                )
        name = control_args.get("name", "")
        ident = control_args.get("ident", "")
        child_ident = control_args.get("child_ident", "")
        depth = control_args.get("depth", 0)
        if name == "":
            name = format(self)
        keys = self.keys()
        keys.sort()
        if print_types and len(keys) == 0:
            print("{}{}: Empty hdf5 group.".format(ident, name))
        elif print_types and (max_depth >= 0 and depth >= max_depth):
            print("{}{}: {}".format(ident, name, self))
        else:
            print("{}{}".format(ident, name))
        if max_depth == -1 or depth < max_depth:
            if is_numeric_index(keys) and not print_types:
                keys.sort()
                print("{}[{} ... {}]".format(child_ident + "╰───", keys[0], keys[-1]))
            else:
                if len(self) > 0:
                    for key in keys[:-1]:
                        try:
                            self[key].tree_view(
                                max_depth=max_depth,
                                print_types=print_types,
                                name=key,
                                ident=child_ident + "├───",
                                child_ident=child_ident + "│   ",
                                depth=depth + 1,
                            )
                        except AttributeError:
                            if print_types:
                                print(
                                    "{}{}: {}".format(
                                        child_ident + "├───", key, type(self[key])
                                    )
                                )
                            else:
                                print("{}{}".format(child_ident + "├───", key))
                    try:
                        self[keys[-1]].tree_view(
                            max_depth=max_depth,
                            print_types=print_types,
                            name=keys[-1],
                            ident=child_ident + "└───",
                            child_ident=child_ident + "    ",
                            depth=depth + 1,
                        )
                    except AttributeError:
                        if print_types:
                            print(
                                "{}{}: {}".format(
                                    child_ident + "╰───", keys[-1], type(self[keys[-1]])
                                )
                            )
                        else:
                            print("{}{}".format(child_ident + "╰───", keys[-1]))

    def close(self):
        """Closes the HDF5 file."""
        self.hdf5.close()
        self.closed = True


# AUXILIARY FUNCTIONS
def is_t(key, sufix):
    if len(key) > len(sufix):
        if key[-len(sufix) :] == sufix:
            return True
    return False


def try_convert_from(d, conversions):
    for t, f, _ in conversions:
        if type(d) == t:
            return f(d), str(t)
    return d, None


def try_convert_to(d, type, conversions):
    for t, _, f in conversions:
        if type == str(t):
            return f(d)
    return d


def is_numeric_index(l):
    new_l = []
    for v in l:
        try:
            new_l.append(int(v))
        except:
            return False
    new_l.sort()
    if len(new_l) == 0:
        return False
    if new_l[0] != 0:
        return False
    last_i = new_l[0]
    for i in new_l[1:]:
        if i - last_i != 1:
            return False
        last_i = i
    return True
