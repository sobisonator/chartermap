# CRM
The Conceptual Reference Model (CRM) of CharterDB is based on [CIDOC CRM](https://cidoc-crm.org/)

At time of writing, the CIDOC CRM version accessed is [7.1.3](https://www.cidoc-crm.org/sites/default/files/cidoc_crm_version_7.1.3.pdf)

All markups in CharterDB refer implicitly, by their association with a portion of the text, to instances of CIDOC's [E33 Linguistic Object](https://cidoc-crm.org/Entity/e33-linguistic-object/version-7.1.1)

Creating a markup implictly assigns the E33 instance a [P67 refers to](https://cidoc-crm.org/Property/p67-refers-to/version-6.2.1) property.

Every text is made up of a series of [E90 symbolic objects](https://cidoc-crm.org/Entity/e90-symbolic-object/version-7.1.1]) which are stored as individual objects in the database.

We do not use E62 string because the native format of the charters is not digital, the transcriptions are a matter of convenience.