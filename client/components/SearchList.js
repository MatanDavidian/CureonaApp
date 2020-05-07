import React, { useState, useEffect } from 'react'
import {
    View,
    Text,
    StyleSheet,
    FlatList,
    Keyboard,
    TouchableWithoutFeedback,
} from 'react-native';
import SearchItem from './SearchItem/SearchItem';
import { ScrollView, TextInput } from 'react-native-gesture-handler';
import text from '../constants/text';

const SearchList = props => {
    const DATA = props.navigation.getParam('storeList')
    const action =
        props.navigation.getParam('USERTYPE') === text.type.admin ?
            text.decisions.adminChanges
            :
            text.decisions.makeAnAppointment
    const [searchInput, setSearchInput] = useState('');
    const [filteredData, setFilteredData] = useState([]);
    const filterData = () => {
        console.log(filteredData)
        const nameMatch = DATA.filter(item => item.name.toUpperCase().includes(searchInput.toUpperCase()));
        const keyMatch = DATA.filter(item => item.keywords.filter(keyword => keyword.toUpperCase().includes(searchInput.toUpperCase())).length > 0)
        const displayIds = [...new Set([...nameMatch.map(item => item.id), ...keyMatch.map(item => item.id)])];
        const display = DATA.filter(item => displayIds.indexOf(item.id) > -1)


        setFilteredData([...display]);
    }

    useEffect(() => {
        filterData();
    }, [searchInput])

    console.log("searchlist : ", props.username)
    return (

        <View style={styles.container}>
            <TouchableWithoutFeedback onPress={Keyboard.dismiss} accessible={false}>
                <View style={styles.inputContainer}>
                    <Text style={styles.label}>{"Seach Business"}</Text>
                    <TextInput
                        style={styles.input}
                        value={searchInput}
                        onChangeText={text => setSearchInput(text)}
                    />
                </View>
            </TouchableWithoutFeedback>
            <FlatList
                style={styles.gap}
                data={filteredData}
                renderItem={({ item }) =>
                    <SearchItem
                        title={item.name}
                        address={item.address}
                        keywords={item.keywords}
                        pressAction={action}
                        content={item}
                        navigation={props.navigation}
                        username={props.username}
                        id={item.id}
                    />}
                keyExtractor={item => item.id}
            />
            <TouchableWithoutFeedback onPress={Keyboard.dismiss} accessible={false}>
                <View style={styles.gap} />
            </TouchableWithoutFeedback>
        </View>
    )
}

const styles = StyleSheet.create({
    title: {
        fontSize: 16,
        fontWeight: 'bold',
    },
    container: {
        padding: 20
    },
    listConainer: {

    },
    label: {
        marginVertical: 8,
        fontWeight: 'bold',
        fontSize: 20,
    },
    input: {
        paddingHorizontal: 2,
        paddingVertical: 5,
        borderBottomColor: '#ccc',
        borderBottomWidth: 1
    },
    gap: {
        marginBottom: 100,
    }
})

export default SearchList;