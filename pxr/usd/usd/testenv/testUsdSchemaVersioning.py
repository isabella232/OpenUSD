#!/pxrpythonsubst
#
# Copyright 2022 Pixar
#
# Licensed under the Apache License, Version 2.0 (the "Apache License")
# with the following modification; you may not use this file except in
# compliance with the Apache License and the following modification to it:
# Section 6. Trademarks. is deleted and replaced with:
#
# 6. Trademarks. This License does not grant permission to use the trade
#    names, trademarks, service marks, or product names of the Licensor
#    and its affiliates, except as required to comply with Section 4(c) of
#    the License and to reproduce the content of the NOTICE file.
#
# You may obtain a copy of the Apache License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the Apache License with the above modification is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied. See the Apache License for the specific
# language governing permissions and limitations under the Apache License.

import os, unittest
from pxr import Plug, Usd, Tf

class TestUsdSchemaRegistry(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pr = Plug.Registry()
        testPlugins = pr.RegisterPlugins(os.path.abspath("resources"))
        assert len(testPlugins) == 1, \
            "Failed to load expected test plugin"
        assert testPlugins[0].name == "testUsdSchemaVersioning", \
            "Failed to load expected test plugin"
    
        # Types representing three versions of a typed schema registered for 
        # this test.
        cls.BasicVersion0Type = Tf.Type.FindByName(
            'TestUsdSchemaVersioningTestBasicVersioned')
        cls.BasicVersion1Type = Tf.Type.FindByName(
            'TestUsdSchemaVersioningTestBasicVersioned_1')
        cls.BasicVersion2Type = Tf.Type.FindByName(
            'TestUsdSchemaVersioningTestBasicVersioned_2')
        assert(not cls.BasicVersion0Type.isUnknown)
        assert(not cls.BasicVersion1Type.isUnknown)
        assert(not cls.BasicVersion2Type.isUnknown)

        # Types representing three versions of a single-apply API schema
        # registered for this test.
        cls.SingleApiVersion0Type = Tf.Type.FindByName(
            'TestUsdSchemaVersioningTestVersionedSingleApplyAPI')
        cls.SingleApiVersion1Type = Tf.Type.FindByName(
            'TestUsdSchemaVersioningTestVersionedSingleApplyAPI_1')
        cls.SingleApiVersion2Type = Tf.Type.FindByName(
            'TestUsdSchemaVersioningTestVersionedSingleApplyAPI_2')
        assert(not cls.SingleApiVersion0Type.isUnknown)
        assert(not cls.SingleApiVersion1Type.isUnknown)
        assert(not cls.SingleApiVersion2Type.isUnknown)

        # Types representing three versions of a multiple-apply API schema
        # registered for this test.
        cls.MultiApiVersion0Type = Tf.Type.FindByName(
            'TestUsdSchemaVersioningTestVersionedMultiApplyAPI')
        cls.MultiApiVersion1Type = Tf.Type.FindByName(
            'TestUsdSchemaVersioningTestVersionedMultiApplyAPI_1')
        cls.MultiApiVersion2Type = Tf.Type.FindByName(
            'TestUsdSchemaVersioningTestVersionedMultiApplyAPI_2')
        assert(not cls.MultiApiVersion0Type.isUnknown)
        assert(not cls.MultiApiVersion1Type.isUnknown)
        assert(not cls.MultiApiVersion2Type.isUnknown)


    def test_ParseFamilyAndVersion(self):
        """Tests the parsing of family and version values from schema 
        identifier values"""

        # Helper for verifying the parsed identifier produces expected families
        # and versions.
        def _VerifyVersionParsing(identifier, family, version, 
                                  expectFamilyAllowed=True, 
                                  expectIdentifierAllowed=True):
            # Verify the identifier can be parsed into the given family and
            # version
            self.assertEqual(
                Usd.SchemaRegistry.ParseSchemaFamilyAndVersionFromIdentifier(
                    identifier),
                (family, version))

            # Verify the allowed-ness of the parsed family.
            isFamilyAllowed = Usd.SchemaRegistry.IsAllowedSchemaFamily(family)
            if expectFamilyAllowed:
                self.assertTrue(isFamilyAllowed)
            else:
                self.assertFalse(isFamilyAllowed)

            # Verify the allowed-ness of the identifier.
            isIdentifierAllowed = \
                Usd.SchemaRegistry.IsAllowedSchemaIdentifier(identifier)
            if expectIdentifierAllowed:
                self.assertTrue(isIdentifierAllowed)
            else:
                self.assertFalse(isIdentifierAllowed)

            # Make the identifier from the family and version and verify that it
            # matches the identifier...
            identifierFromFamilyAndVersion = \
                Usd.SchemaRegistry.MakeSchemaIdentifierForFamilyAndVersion(
                    family, version)
            # ...except if the parsed family is allowed but the identifier is 
            # not, this  will because the identifier is not the identifier that 
            # family and version produce, so it won't match. 
            if expectFamilyAllowed and not expectIdentifierAllowed:
                self.assertNotEqual(identifierFromFamilyAndVersion, identifier)
            else:
                self.assertEqual(identifierFromFamilyAndVersion, identifier)

        # Parse allowed versioned identifiers.
        _VerifyVersionParsing("Foo", "Foo", 0)        
        _VerifyVersionParsing("Foo_1", "Foo", 1)        
        _VerifyVersionParsing("Foo_20", "Foo", 20)        

        _VerifyVersionParsing("Foo_Bar", "Foo_Bar", 0)        
        _VerifyVersionParsing("Foo_Bar_1", "Foo_Bar", 1)        
        _VerifyVersionParsing("Foo_Bar_20", "Foo_Bar", 20)        

        _VerifyVersionParsing("Foo_", "Foo_", 0)        
        _VerifyVersionParsing("Foo__1", "Foo_", 1)        
        _VerifyVersionParsing("Foo__20", "Foo_", 20)        

        _VerifyVersionParsing("Foo_1_", "Foo_1_", 0)        
        _VerifyVersionParsing("Foo_1__1", "Foo_1_", 1)        
        _VerifyVersionParsing("Foo_1__20", "Foo_1_", 20)      

        _VerifyVersionParsing("_Foo", "_Foo", 0)        
        _VerifyVersionParsing("_Foo_1", "_Foo", 1)        
        _VerifyVersionParsing("_Foo_20", "_Foo", 20)        

        # Parse bad versioned identifiers that parse into unallowed families.
        _VerifyVersionParsing("_1", "", 1, 
            expectFamilyAllowed=False, expectIdentifierAllowed=False)  
        _VerifyVersionParsing("Foo_20_1", "Foo_20", 1, 
            expectFamilyAllowed=False, expectIdentifierAllowed=False)  
        _VerifyVersionParsing("Foo_22.5", "Foo_22.5", 0, 
            expectFamilyAllowed=False, expectIdentifierAllowed=False)  
        _VerifyVersionParsing("Foo_-1", "Foo_-1", 0, 
            expectFamilyAllowed=False, expectIdentifierAllowed=False)  
        _VerifyVersionParsing("", "", 0, 
            expectFamilyAllowed=False, expectIdentifierAllowed=False)  

        # Parse bad versioned identifiers that parse into allowed families,
        # but don't use the expected suffix format for that version.
        _VerifyVersionParsing("Foo_0", "Foo", 0, 
            expectFamilyAllowed=True, expectIdentifierAllowed=False)  
        _VerifyVersionParsing("Foo_01", "Foo", 1, 
            expectFamilyAllowed=True, expectIdentifierAllowed=False)  

    def test_SchemaInfo(self):
        """Tests getting SchemaInfo from the schema registry"""

        # The expected values from the SchemaInfo struct for each schema type.
        expectedVersion0Info = {
            "type" : self.BasicVersion0Type,
            "identifier" : 'TestBasicVersioned',
            "kind" : Usd.SchemaKind.ConcreteTyped,
            "family" : 'TestBasicVersioned',
            "version" : 0
        }

        expectedVersion1Info = {
            "type" : self.BasicVersion1Type,
            "identifier" : 'TestBasicVersioned_1',
            "kind" : Usd.SchemaKind.ConcreteTyped,
            "family" : 'TestBasicVersioned',
            "version" : 1
        }

        expectedVersion2Info = {
            "type" : self.BasicVersion2Type,
            "identifier" : 'TestBasicVersioned_2',
            "kind" : Usd.SchemaKind.ConcreteTyped,
            "family" : 'TestBasicVersioned',
            "version" : 2
        }

        # Simple helper that verifies a SchemaInfo matches expected values.
        def _VerifySchemaInfo(schemaInfo, expected) :
            self.assertEqual(schemaInfo.type, expected["type"])
            self.assertEqual(schemaInfo.identifier, expected["identifier"])
            self.assertEqual(schemaInfo.kind, expected["kind"])
            self.assertEqual(schemaInfo.family, expected["family"])
            self.assertEqual(schemaInfo.version, expected["version"])

        # Find schema by TfType.
        _VerifySchemaInfo(
            Usd.SchemaRegistry.FindSchemaInfo(self.BasicVersion0Type),
            expectedVersion0Info)
        _VerifySchemaInfo(
            Usd.SchemaRegistry.FindSchemaInfo(self.BasicVersion1Type),
            expectedVersion1Info)
        _VerifySchemaInfo(
            Usd.SchemaRegistry.FindSchemaInfo(self.BasicVersion2Type),
            expectedVersion2Info)

        # Find schema by identifier.
        _VerifySchemaInfo(
            Usd.SchemaRegistry.FindSchemaInfo('TestBasicVersioned'),
            expectedVersion0Info)
        _VerifySchemaInfo(
            Usd.SchemaRegistry.FindSchemaInfo('TestBasicVersioned_1'),
            expectedVersion1Info)
        _VerifySchemaInfo(
            Usd.SchemaRegistry.FindSchemaInfo('TestBasicVersioned_2'),
            expectedVersion2Info)

        # Find schema by family and version.
        _VerifySchemaInfo(
            Usd.SchemaRegistry.FindSchemaInfo('TestBasicVersioned', 0),
            expectedVersion0Info)
        _VerifySchemaInfo(
            Usd.SchemaRegistry.FindSchemaInfo('TestBasicVersioned', 1),
            expectedVersion1Info)
        _VerifySchemaInfo(
            Usd.SchemaRegistry.FindSchemaInfo('TestBasicVersioned', 2),
            expectedVersion2Info)

        # Simple helper that verifies a list of SchemaInfo all match an expected
        # values.
        def _VerifySchemaInfoList(schemaInfoList, expectedList) :
            self.assertEqual(len(schemaInfoList), len(expectedList))
            for schemaInfo, expected in zip(schemaInfoList, expectedList):
                _VerifySchemaInfo(schemaInfo, expected)

        # Find all schemas in a family
        _VerifySchemaInfoList(
            Usd.SchemaRegistry.FindSchemaInfosInFamily('TestBasicVersioned'),
            [expectedVersion2Info, expectedVersion1Info, expectedVersion0Info])

        # Find filtered schemas in a family: VersionPolicy = All
        _VerifySchemaInfoList(
            Usd.SchemaRegistry.FindSchemaInfosInFamily(
                'TestBasicVersioned', 0, 
                Usd.SchemaRegistry.VersionPolicy.All),
            [expectedVersion2Info, expectedVersion1Info, expectedVersion0Info])
        _VerifySchemaInfoList(
            Usd.SchemaRegistry.FindSchemaInfosInFamily(
                'TestBasicVersioned', 1,
                Usd.SchemaRegistry.VersionPolicy.All),
            [expectedVersion2Info, expectedVersion1Info, expectedVersion0Info])
        _VerifySchemaInfoList(
            Usd.SchemaRegistry.FindSchemaInfosInFamily(
                'TestBasicVersioned', 2, Usd.SchemaRegistry.VersionPolicy.All),
            [expectedVersion2Info, expectedVersion1Info, expectedVersion0Info])

        # Find filtered schemas in a family: VersionPolicy = GreaterThan
        _VerifySchemaInfoList(
            Usd.SchemaRegistry.FindSchemaInfosInFamily(
                'TestBasicVersioned', 0,
                Usd.SchemaRegistry.VersionPolicy.GreaterThan),
            [expectedVersion2Info, expectedVersion1Info, ])
        _VerifySchemaInfoList(
            Usd.SchemaRegistry.FindSchemaInfosInFamily(
                'TestBasicVersioned', 1,
                Usd.SchemaRegistry.VersionPolicy.GreaterThan),
            [expectedVersion2Info])
        _VerifySchemaInfoList(
            Usd.SchemaRegistry.FindSchemaInfosInFamily(
                'TestBasicVersioned', 2,
                Usd.SchemaRegistry.VersionPolicy.GreaterThan),
            [])

        # Find filtered schemas in a family: VersionPolicy = GreaterThanOrEqual
        _VerifySchemaInfoList(
            Usd.SchemaRegistry.FindSchemaInfosInFamily(
                'TestBasicVersioned', 0,
                Usd.SchemaRegistry.VersionPolicy.GreaterThanOrEqual),
            [expectedVersion2Info, expectedVersion1Info, expectedVersion0Info])
        _VerifySchemaInfoList(
            Usd.SchemaRegistry.FindSchemaInfosInFamily(
                'TestBasicVersioned', 1,
                Usd.SchemaRegistry.VersionPolicy.GreaterThanOrEqual),
            [expectedVersion2Info, expectedVersion1Info])
        _VerifySchemaInfoList(
            Usd.SchemaRegistry.FindSchemaInfosInFamily(
                'TestBasicVersioned', 2, 
                Usd.SchemaRegistry.VersionPolicy.GreaterThanOrEqual),
            [expectedVersion2Info])

        # Find filtered schemas in a family: VersionPolicy = LessThan
        _VerifySchemaInfoList(
            Usd.SchemaRegistry.FindSchemaInfosInFamily(
                'TestBasicVersioned', 0, 
                Usd.SchemaRegistry.VersionPolicy.LessThan),
            [])
        _VerifySchemaInfoList(
            Usd.SchemaRegistry.FindSchemaInfosInFamily(
                'TestBasicVersioned', 1, 
                Usd.SchemaRegistry.VersionPolicy.LessThan),
            [expectedVersion0Info])
        _VerifySchemaInfoList(
            Usd.SchemaRegistry.FindSchemaInfosInFamily(
                'TestBasicVersioned', 2,
                Usd.SchemaRegistry.VersionPolicy.LessThan),
            [expectedVersion1Info, expectedVersion0Info])

        # Find filtered schemas in a family: VersionPolicy = LessThanOrEqual
        _VerifySchemaInfoList(
            Usd.SchemaRegistry.FindSchemaInfosInFamily(
                'TestBasicVersioned', 0,
                Usd.SchemaRegistry.VersionPolicy.LessThanOrEqual),
            [expectedVersion0Info])
        _VerifySchemaInfoList(
            Usd.SchemaRegistry.FindSchemaInfosInFamily(
                'TestBasicVersioned', 1,
                Usd.SchemaRegistry.VersionPolicy.LessThanOrEqual),
            [expectedVersion1Info, expectedVersion0Info])
        _VerifySchemaInfoList(
            Usd.SchemaRegistry.FindSchemaInfosInFamily(
                'TestBasicVersioned', 2,
                Usd.SchemaRegistry.VersionPolicy.LessThanOrEqual),
            [expectedVersion2Info, expectedVersion1Info, expectedVersion0Info])
    
        # Edge cases:
        # Verify that calling FindSchemaInfo and FindSchemaInfosInFamily, 
        # passing a registered non-zero versioned schema identifier as the 
        # family, does not return any schema info.
        validVersionedIdentifier = 'TestBasicVersioned_1'
        # Find by identifier is valid
        self.assertIsNotNone(
            Usd.SchemaRegistry.FindSchemaInfo(validVersionedIdentifier))
        # Find by family and version 0 is not valid
        self.assertIsNone(
            Usd.SchemaRegistry.FindSchemaInfo(validVersionedIdentifier, 0))
        # Find all in family produces no schemas.
        self.assertEqual(
            Usd.SchemaRegistry.FindSchemaInfosInFamily(validVersionedIdentifier), 
            [])
        self.assertEqual(
            Usd.SchemaRegistry.FindSchemaInfosInFamily(
                validVersionedIdentifier, 0, 
                Usd.SchemaRegistry.VersionPolicy.All), 
            [])

    def test_PrimIsA(self):
        """Tests all Usd.Prim API for querying if a prim 'IsA' with 
           versioned typed schemas"""        

        # The expected values from the SchemaInfo struct for each schema type.
        expectedVersion0Info = {
            "type" : self.BasicVersion0Type,
            "identifier" : 'TestBasicVersioned',
            "kind" : Usd.SchemaKind.ConcreteTyped,
            "family" : 'TestBasicVersioned',
            "version" : 0
        }

        expectedVersion1Info = {
            "type" : self.BasicVersion1Type,
            "identifier" : 'TestBasicVersioned_1',
            "kind" : Usd.SchemaKind.ConcreteTyped,
            "family" : 'TestBasicVersioned',
            "version" : 1
        }

        expectedVersion2Info = {
            "type" : self.BasicVersion2Type,
            "identifier" : 'TestBasicVersioned_2',
            "kind" : Usd.SchemaKind.ConcreteTyped,
            "family" : 'TestBasicVersioned',
            "version" : 2
        }

        # Create a prim typed with each version of the schema.
        stage = Usd.Stage.CreateInMemory()
        primV0 = stage.DefinePrim("/Prim", "TestBasicVersioned")
        primV1 = stage.DefinePrim("/Prim1", "TestBasicVersioned_1")
        primV2 = stage.DefinePrim("/Prim2", "TestBasicVersioned_2")

        self.assertTrue(primV0)
        self.assertTrue(primV1)
        self.assertTrue(primV2)

        # Verifies that IsA is true for the prim, using all three input types,
        # for the schema specified in schemaInfo.
        def _VerifyIsA(prim, schemaInfo):
            # By TfType
            self.assertTrue(prim.IsA(schemaInfo["type"]))
            # By Identifier
            self.assertTrue(prim.IsA(schemaInfo["identifier"]))
            # By Family and Version
            self.assertTrue(prim.IsA(schemaInfo["family"], 
                                     schemaInfo["version"]))

        # Verifies that IsA is false for the prim, using all three input types,
        # for the schema specified in schemaInfo.
        def _VerifyNotIsA(prim, schemaInfo):
            # By TfType
            self.assertFalse(prim.IsA(schemaInfo["type"]))
            # By Identifier
            self.assertFalse(prim.IsA(schemaInfo["identifier"]))
            # By Family and Version
            self.assertFalse(prim.IsA(schemaInfo["family"], 
                                      schemaInfo["version"]))

        # For each prim verify that all IsA calls return true for the schema
        # inputs related to its type and false for the schema inputs that are 
        # not.
        _VerifyIsA(primV0, expectedVersion0Info)
        _VerifyNotIsA(primV0, expectedVersion1Info)
        _VerifyNotIsA(primV0, expectedVersion2Info)

        _VerifyNotIsA(primV1, expectedVersion0Info)
        _VerifyIsA(primV1, expectedVersion1Info)
        _VerifyNotIsA(primV1, expectedVersion2Info)

        _VerifyNotIsA(primV2, expectedVersion0Info)
        _VerifyNotIsA(primV2, expectedVersion1Info)
        _VerifyIsA(primV2, expectedVersion2Info)

    # Verifies that a prim HasAPI, using all three input types, for the schema 
    # specified in schemaInfo.
    def _VerifyHasAPI(self, prim, schemaInfo):
        # By TfType
        self.assertTrue(prim.HasAPI(schemaInfo["type"]))
        # By Identifier
        self.assertTrue(prim.HasAPI(schemaInfo["identifier"]))
        # By Family and Version
        self.assertTrue(prim.HasAPI(schemaInfo["family"], 
                                    schemaInfo["version"]))

    # Verifies that a prim does NOT HasAPI, using all three input types, for the
    # schema specified in schemaInfo.
    def _VerifyNotHasAPI(self, prim, schemaInfo):
        # By TfType
        self.assertFalse(prim.HasAPI(schemaInfo["type"]))
        # By Identifier
        self.assertFalse(prim.HasAPI(schemaInfo["identifier"]))
        # By Family and Version
        self.assertFalse(prim.HasAPI(schemaInfo["family"], 
                                        schemaInfo["version"]))

    # Verifies that a prim HasAPI with the specified instance name, using all 
    # three input types, for the schema specified in schemaInfo.
    def _VerifyHasAPIInstance(self, prim, schemaInfo, instanceName):
        # By TfType
        self.assertTrue(prim.HasAPI(schemaInfo["type"], instanceName))
        # By Identifier
        self.assertTrue(prim.HasAPI(schemaInfo["identifier"], instanceName))
        # By Family and Version
        self.assertTrue(prim.HasAPI(schemaInfo["family"], 
                                    schemaInfo["version"],
                                    instanceName))

    # Verifies that a prim does NOT HasAPI with the specified instance name, 
    # using all three input types, for the schema specified in schemaInfo.
    def _VerifyNotHasAPIInstance(self, prim, schemaInfo, instanceName):
        # By TfType
        self.assertFalse(prim.HasAPI(schemaInfo["type"], instanceName))
        # By Identifier
        self.assertFalse(prim.HasAPI(schemaInfo["identifier"], instanceName))
        # By Family and Version
        self.assertFalse(prim.HasAPI(schemaInfo["family"], 
                                    schemaInfo["version"], instanceName))

    def test_PrimHasAPI_SingleApply(self):
        """Tests all Usd.Prim API for querying if a prim 'HasAPI' with 
           versioned single-apply API schemas"""        

        # The expected values from the SchemaInfo struct for each schema type.
        expectedVersion0Info = {
            "type" : self.SingleApiVersion0Type,
            "identifier" : 'TestVersionedSingleApplyAPI',
            "kind" : Usd.SchemaKind.SingleApplyAPI,
            "family" : 'TestVersionedSingleApplyAPI',
            "version" : 0
        }

        expectedVersion1Info = {
            "type" : self.SingleApiVersion1Type,
            "identifier" : 'TestVersionedSingleApplyAPI_1',
            "kind" : Usd.SchemaKind.SingleApplyAPI,
            "family" : 'TestVersionedSingleApplyAPI',
            "version" : 1
        }

        expectedVersion2Info = {
            "type" : self.SingleApiVersion2Type,
            "identifier" : 'TestVersionedSingleApplyAPI_2',
            "kind" : Usd.SchemaKind.SingleApplyAPI,
            "family" : 'TestVersionedSingleApplyAPI',
            "version" : 2
        }

        # Create a prim each with a different version of the schema applied.
        stage = Usd.Stage.CreateInMemory()
        primV0 = stage.DefinePrim("/Prim")
        primV1 = stage.DefinePrim("/Prim1")
        primV2 = stage.DefinePrim("/Prim2")

        self.assertTrue(primV0)
        self.assertTrue(primV1)
        self.assertTrue(primV2)

        primV0.ApplyAPI(self.SingleApiVersion0Type)
        primV1.ApplyAPI(self.SingleApiVersion1Type)
        primV2.ApplyAPI(self.SingleApiVersion2Type)

        # For each prim verify that all HasAPI calls return true for the schema
        # inputs related to its applied API type and false for the schema inputs
        # that are not.
        self._VerifyHasAPI(primV0, expectedVersion0Info)
        self._VerifyNotHasAPI(primV0, expectedVersion1Info)
        self._VerifyNotHasAPI(primV0, expectedVersion2Info)

        self._VerifyNotHasAPI(primV1, expectedVersion0Info)
        self._VerifyHasAPI(primV1, expectedVersion1Info)
        self._VerifyNotHasAPI(primV1, expectedVersion2Info)

        self._VerifyNotHasAPI(primV2, expectedVersion0Info)
        self._VerifyNotHasAPI(primV2, expectedVersion1Info)
        self._VerifyHasAPI(primV2, expectedVersion2Info)

    def test_PrimHasAPI_MultiApply(self):
        """Tests all Usd.Prim API for querying if a prim 'HasAPI' with 
           versioned multiple-apply API schemas"""        

        # The expected values from the SchemaInfo struct for each schema type.
        expectedVersion0Info = {
            "type" : self.MultiApiVersion0Type,
            "identifier" : 'TestVersionedMultiApplyAPI',
            "kind" : Usd.SchemaKind.MultipleApplyAPI,
            "family" : 'TestVersionedMultiApplyAPI',
            "version" : 0
        }

        expectedVersion1Info = {
            "type" : self.MultiApiVersion1Type,
            "identifier" : 'TestVersionedMultiApplyAPI_1',
            "kind" : Usd.SchemaKind.MultipleApplyAPI,
            "family" : 'TestVersionedMultiApplyAPI',
            "version" : 1
        }

        expectedVersion2Info = {
            "type" : self.MultiApiVersion2Type,
            "identifier" : 'TestVersionedMultiApplyAPI_2',
            "kind" : Usd.SchemaKind.MultipleApplyAPI,
            "family" : 'TestVersionedMultiApplyAPI',
            "version" : 2
        }

        # Create a prim each with a different versions and instances of the 
        # schema applied.
        stage = Usd.Stage.CreateInMemory()
        primV0 = stage.DefinePrim("/Prim")
        primV1 = stage.DefinePrim("/Prim1")
        primV2 = stage.DefinePrim("/Prim2")

        self.assertTrue(primV0)
        self.assertTrue(primV1)
        self.assertTrue(primV2)

        # The schemas are applied for combinations of version and instance:
        # prim0 -> "API:foo", "API_2:bar"
        # prim1 -> "API_1:foo", "API_1:bar"
        # prim2 -> "API_2:foo", "API:bar"
        self.assertTrue(primV0.ApplyAPI(self.MultiApiVersion0Type, "foo"))
        self.assertTrue(primV1.ApplyAPI(self.MultiApiVersion1Type, "foo"))
        self.assertTrue(primV2.ApplyAPI(self.MultiApiVersion2Type, "foo"))

        self.assertTrue(primV0.ApplyAPI(self.MultiApiVersion2Type, "bar"))
        self.assertTrue(primV1.ApplyAPI(self.MultiApiVersion1Type, "bar"))
        self.assertTrue(primV2.ApplyAPI(self.MultiApiVersion0Type, "bar"))

        # Helper for verifying all inputs HasAPI and the expected return values
        # around the instance for the given schema it is expected to have
        def _VerifyHasAPIInstances(prim, schemaInfo, expectedHasInstanceNames):
            # Verify the return value for all calls to HasAPI without a 
            # specified instance name. We expect these to return true iff we
            # expect the prim to have any instances of the schema.
            if expectedHasInstanceNames:
                self._VerifyHasAPI(prim, schemaInfo)
            else:
                self._VerifyNotHasAPI(prim, schemaInfo)
            
            # Verify all calls to HasAPI "foo" return true iff we expect the
            # prim to have a "foo" instance of the schema.
            if "foo" in expectedHasInstanceNames:
                self._VerifyHasAPIInstance(prim, schemaInfo, "foo")
            else:
                self._VerifyNotHasAPIInstance(prim, schemaInfo, "foo")

            # Verify all calls to HasAPI "bar" return true iff we expect the
            # prim to have a "foo" instance of the schema.
            if "bar" in expectedHasInstanceNames:
                self._VerifyHasAPIInstance(prim, schemaInfo, "bar")
            else:
                self._VerifyNotHasAPIInstance(prim, schemaInfo, "bar")

        # For each prim verify that all HasAPI calls return true for the schema
        # inputs related to the applied API schema instances it was applied with
        # and false for everything else.
        _VerifyHasAPIInstances(primV0, expectedVersion0Info, ["foo"])
        _VerifyHasAPIInstances(primV0, expectedVersion1Info, [])
        _VerifyHasAPIInstances(primV0, expectedVersion2Info, ["bar"])

        _VerifyHasAPIInstances(primV1, expectedVersion0Info, [])
        _VerifyHasAPIInstances(primV1, expectedVersion1Info, ["foo", "bar"])
        _VerifyHasAPIInstances(primV1, expectedVersion2Info, [])

        _VerifyHasAPIInstances(primV2, expectedVersion0Info, ["bar"])
        _VerifyHasAPIInstances(primV2, expectedVersion1Info, [])
        _VerifyHasAPIInstances(primV2, expectedVersion2Info, ["foo"])

    def test_ApplyRemoveAPI(self):
        """Tests all Usd.Prim API for applying and removing API schema with 
           versioned API schemas"""        

        # The expected values from the SchemaInfo struct for each single-apply
        # schema type.
        expectedSingleApplyVersion0Info = {
            "type" : self.SingleApiVersion0Type,
            "identifier" : 'TestVersionedSingleApplyAPI',
            "kind" : Usd.SchemaKind.SingleApplyAPI,
            "family" : 'TestVersionedSingleApplyAPI',
            "version" : 0
        }

        expectedSingleApplyVersion1Info = {
            "type" : self.SingleApiVersion1Type,
            "identifier" : 'TestVersionedSingleApplyAPI_1',
            "kind" : Usd.SchemaKind.SingleApplyAPI,
            "family" : 'TestVersionedSingleApplyAPI',
            "version" : 1
        }

        expectedSingleApplyVersion2Info = {
            "type" : self.SingleApiVersion2Type,
            "identifier" : 'TestVersionedSingleApplyAPI_2',
            "kind" : Usd.SchemaKind.SingleApplyAPI,
            "family" : 'TestVersionedSingleApplyAPI',
            "version" : 2
        }

        # The expected values from the SchemaInfo struct for each multiple-apply
        # schema type.
        expectedMultiApplyVersion0Info = {
            "type" : self.MultiApiVersion0Type,
            "identifier" : 'TestVersionedMultiApplyAPI',
            "kind" : Usd.SchemaKind.MultipleApplyAPI,
            "family" : 'TestVersionedMultiApplyAPI',
            "version" : 0
        }

        expectedMultiApplyVersion1Info = {
            "type" : self.MultiApiVersion1Type,
            "identifier" : 'TestVersionedMultiApplyAPI_1',
            "kind" : Usd.SchemaKind.MultipleApplyAPI,
            "family" : 'TestVersionedMultiApplyAPI',
            "version" : 1
        }

        expectedMultiApplyVersion2Info = {
            "type" : self.MultiApiVersion2Type,
            "identifier" : 'TestVersionedMultiApplyAPI_2',
            "kind" : Usd.SchemaKind.MultipleApplyAPI,
            "family" : 'TestVersionedMultiApplyAPI',
            "version" : 2
        }

        # Verifies that a CanApplyAPI returns true for a prim, using all three 
        # input types, for the schema specified in schemaInfo.
        def _VerifyCanApplyAPI(prim, schemaInfo):
            # By TfType
            self.assertTrue(prim.CanApplyAPI(schemaInfo["type"]))
            # By Identifier
            self.assertTrue(prim.CanApplyAPI(schemaInfo["identifier"]))
            # By Family and Version
            self.assertTrue(prim.CanApplyAPI(schemaInfo["family"], 
                                             schemaInfo["version"]))

        # Verifies that a CanApplyAPI returns false for a prim, using all three 
        # input types, for the schema specified in schemaInfo.
        def _VerifyNotCanApplyAPI(prim, schemaInfo):
            # By TfType
            self.assertFalse(prim.CanApplyAPI(schemaInfo["type"]))
            # By Identifier
            self.assertFalse(prim.CanApplyAPI(schemaInfo["identifier"]))
            # By Family and Version
            self.assertFalse(prim.CanApplyAPI(schemaInfo["family"], 
                                              schemaInfo["version"]))

        # Verifies that a CanApplyAPI with the given instance name returns true
        # for a prim, using all three input types, for the schema specified in
        # schemaInfo.
        def _VerifyCanApplyAPIInstance(prim, schemaInfo, instanceName):
            # By TfType
            self.assertTrue(prim.CanApplyAPI(schemaInfo["type"], instanceName))
            # By Identifier
            self.assertTrue(prim.CanApplyAPI(schemaInfo["identifier"], instanceName))
            # By Family and Version
            self.assertTrue(prim.CanApplyAPI(schemaInfo["family"], 
                                             schemaInfo["version"], instanceName))

        # Verifies that a CanApplyAPI with the given instance name returns false
        # for a prim, using all three input types, for the schema specified in
        # schemaInfo.
        def _VerifyNotCanApplyAPIInstance(prim, schemaInfo, instanceName):
            # By TfType
            self.assertFalse(prim.CanApplyAPI(schemaInfo["type"], instanceName))
            # By Identifier
            self.assertFalse(prim.CanApplyAPI(schemaInfo["identifier"], instanceName))
            # By Family and Version
            self.assertFalse(prim.CanApplyAPI(schemaInfo["family"], 
                                              schemaInfo["version"], instanceName))

        # Verifies applying and removing a single-apply API schema by different
        # combinations of the available input types.
        def _VerifyApplyAndRemoveAPI(prim, schemaInfo):
            # The schema should start unapplied.
            self._VerifyNotHasAPI(prim, schemaInfo)

            # Verify Apply by type
            self.assertTrue(prim.ApplyAPI(schemaInfo["type"]))
            self._VerifyHasAPI(prim, schemaInfo)
            # Verify Remove by identifier
            self.assertTrue(prim.RemoveAPI(schemaInfo["identifier"]))
            self._VerifyNotHasAPI(prim, schemaInfo)

            # Verify Apply by identifier
            self.assertTrue(prim.ApplyAPI(schemaInfo["identifier"]))
            self._VerifyHasAPI(prim, schemaInfo)
            # Verify Remove by family and version
            self.assertTrue(prim.RemoveAPI(schemaInfo["family"], 
                                           schemaInfo["version"]))
            self._VerifyNotHasAPI(prim, schemaInfo)

            # Verify Apply by family and version
            self.assertTrue(prim.ApplyAPI(schemaInfo["family"], 
                                          schemaInfo["version"]))
            self._VerifyHasAPI(prim, schemaInfo)
            # Verify Remove by type
            self.assertTrue(prim.RemoveAPI(schemaInfo["type"]))
            self._VerifyNotHasAPI(prim, schemaInfo)

        # Verifies applying and removing a multiple-apply API schema instance by
        # different combinations of the available input types.
        def _VerifyApplyAndRemoveAPIInstance(prim, schemaInfo, instanceName):
            # The instacne of the schema should start unapplied.
            self._VerifyNotHasAPIInstance(prim, schemaInfo, instanceName)

            # Verify Apply by type
            self.assertTrue(prim.ApplyAPI(schemaInfo["type"], instanceName))
            self._VerifyHasAPIInstance(prim, schemaInfo, instanceName)
            # Verify Remove by identifier
            self.assertTrue(prim.RemoveAPI(schemaInfo["identifier"], instanceName))
            self._VerifyNotHasAPIInstance(prim, schemaInfo, instanceName)

            # Verify Apply by identifier
            self.assertTrue(prim.ApplyAPI(schemaInfo["identifier"], instanceName))
            self._VerifyHasAPIInstance(prim, schemaInfo, instanceName)
            # Verify Remove by family and version
            self.assertTrue(prim.RemoveAPI(schemaInfo["family"], 
                                           schemaInfo["version"], instanceName))
            self._VerifyNotHasAPIInstance(prim, schemaInfo, instanceName)

            # Verify Apply by family and version
            self.assertTrue(prim.ApplyAPI(schemaInfo["family"], 
                                          schemaInfo["version"], instanceName))
            self._VerifyHasAPIInstance(prim, schemaInfo, instanceName)
            # Verify Remove by type
            self.assertTrue(prim.RemoveAPI(schemaInfo["type"], instanceName))
            self._VerifyNotHasAPIInstance(prim, schemaInfo, instanceName)

        # Create a prim typed with each version of the typed schema. The type
        # affects the results of CanApplyAPI.
        stage = Usd.Stage.CreateInMemory()
        primV0 = stage.DefinePrim("/Prim", "TestBasicVersioned")
        primV1 = stage.DefinePrim("/Prim1", "TestBasicVersioned_1")
        primV2 = stage.DefinePrim("/Prim2", "TestBasicVersioned_2")

        # Each version of the single apply API has been designated as 
        # "can only apply to" the same version number of the test typed schema.
        # Verify the CanApplyAPI results for each API schema version.
        _VerifyCanApplyAPI(primV0, expectedSingleApplyVersion0Info)
        _VerifyNotCanApplyAPI(primV0, expectedSingleApplyVersion1Info)
        _VerifyNotCanApplyAPI(primV0, expectedSingleApplyVersion2Info)

        _VerifyNotCanApplyAPI(primV1, expectedSingleApplyVersion0Info)
        _VerifyCanApplyAPI(primV1, expectedSingleApplyVersion1Info)
        _VerifyNotCanApplyAPI(primV1, expectedSingleApplyVersion2Info)

        _VerifyNotCanApplyAPI(primV2, expectedSingleApplyVersion0Info)
        _VerifyNotCanApplyAPI(primV2, expectedSingleApplyVersion1Info)
        _VerifyCanApplyAPI(primV2, expectedSingleApplyVersion2Info)

        # Verify ApplyAPI and RemoveAPI for each version of the single apply API
        # schema. Note that CanApplyAPI results do not affect whether an API 
        # schema is successfully applied to prim through ApplyAPI.
        _VerifyApplyAndRemoveAPI(primV0, expectedSingleApplyVersion0Info)
        _VerifyApplyAndRemoveAPI(primV0, expectedSingleApplyVersion1Info)
        _VerifyApplyAndRemoveAPI(primV0, expectedSingleApplyVersion2Info)

        # Each version of the multiple apply API has been designated as 
        # "can only apply to" a subset of the test typed schema's versions as 
        # follows:
        #   API version 0 can only apply to typed schema version 0
        #   API version 1 can only apply to typed schema version 0 and 1
        #   API version 2 can only apply to typed schema version 1 and 2
        #
        # Verify the CanApplyAPI results for each API schema version.
        _VerifyCanApplyAPIInstance(
            primV0, expectedMultiApplyVersion0Info, "foo")
        _VerifyCanApplyAPIInstance(
            primV0, expectedMultiApplyVersion1Info, "foo")
        _VerifyNotCanApplyAPIInstance(
            primV0, expectedMultiApplyVersion2Info, "foo")

        _VerifyNotCanApplyAPIInstance(
            primV1, expectedMultiApplyVersion0Info, "foo")
        _VerifyCanApplyAPIInstance(
            primV1, expectedMultiApplyVersion1Info, "foo")
        _VerifyCanApplyAPIInstance(
            primV1, expectedMultiApplyVersion2Info, "foo")

        _VerifyNotCanApplyAPIInstance(
            primV2, expectedMultiApplyVersion0Info, "foo")
        _VerifyNotCanApplyAPIInstance(
            primV2, expectedMultiApplyVersion1Info, "foo")
        _VerifyCanApplyAPIInstance(
            primV2, expectedMultiApplyVersion2Info, "foo")

        # Verify ApplyAPI and RemoveAPI for each version of the multiple apply 
        # API schema. Note that CanApplyAPI results do not affect whether an API 
        # schema is successfully applied to prim through ApplyAPI.
        _VerifyApplyAndRemoveAPIInstance(
            primV0, expectedMultiApplyVersion0Info, "foo")
        _VerifyApplyAndRemoveAPIInstance(
            primV0, expectedMultiApplyVersion1Info, "foo")
        _VerifyApplyAndRemoveAPIInstance(
            primV0, expectedMultiApplyVersion2Info, "foo")


if __name__ == "__main__":
    unittest.main()
